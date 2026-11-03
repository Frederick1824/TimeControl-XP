import os
import sqlite3
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import RLock

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB = "/data/clocks.db"
SECRET = os.getenv("JWT_SECRET", "dev-secret")
_lock = RLock()
_executor = ThreadPoolExecutor(max_workers=8)

app = FastAPI(title="clock-svc")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: dict):
        disconnected = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(event)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)


manager = ConnectionManager()


def connect():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    return con


def init_db():
    con = connect()
    con.execute("""
        CREATE TABLE IF NOT EXISTS clocks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at REAL,
            elapsed_before_pause REAL NOT NULL DEFAULT 0,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clock_id TEXT NOT NULL,
            action TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    con.commit()
    con.close()


init_db()


class NewClock(BaseModel):
    name: str


class SyncClocks(BaseModel):
    clock_ids: list[str]


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token invalido")

    username = payload.get("sub")
    role = payload.get("role", "USER")

    if not username:
        raise HTTPException(401, "Token invalido")

    return {
        "username": username,
        "role": role
    }


def current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token requerido")

    token = authorization.split(" ", 1)[1]
    return decode_token(token)


def elapsed_for(row: sqlite3.Row) -> float:
    elapsed = float(row["elapsed_before_pause"] or 0)

    if row["status"] == "RUNNING" and row["started_at"] is not None:
        elapsed += time.time() - float(row["started_at"])

    return max(0.0, elapsed)


def serialize(row: sqlite3.Row):
    return {
        "id": row["id"],
        "name": row["name"],
        "owner": row["owner"],
        "status": row["status"],
        "started_at": row["started_at"],
        "base_elapsed": float(row["elapsed_before_pause"] or 0),
        "elapsed": elapsed_for(row),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def require_access(row: sqlite3.Row, user: dict):
    if user["role"] == "ADMIN":
        return

    if row["owner"] != user["username"]:
        raise HTTPException(
            403,
            "No tienes permiso para acceder a este reloj"
        )


def get_clock_row(cid: str) -> sqlite3.Row:
    con = connect()
    row = con.execute(
        "SELECT * FROM clocks WHERE id = ?",
        (cid,)
    ).fetchone()
    con.close()

    if not row:
        raise HTTPException(404, "Reloj no encontrado")

    return row


def add_event(
    con: sqlite3.Connection,
    cid: str,
    action: str,
    username: str
):
    con.execute(
        """
        INSERT INTO events(clock_id, action, username, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (cid, action, username, time.time())
    )


async def notify_change(action: str, clock_id: str, owner: str):
    await manager.broadcast({
        "type": "clock_changed",
        "action": action,
        "clock_id": clock_id,
        "owner": owner,
        "timestamp": time.time()
    })


@app.websocket("/ws")
async def websocket_updates(websocket: WebSocket, token: str):
    try:
        user = decode_token(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)

    await websocket.send_json({
        "type": "connected",
        "username": user["username"],
        "role": user["role"]
    })

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/health")
def health():
    return {
        "ok": True,
        "websocket_clients": len(manager.active_connections)
    }


@app.get("/time")
def server_time():
    return {"server_time_ms": time.time() * 1000}


@app.post("/clocks")
async def create_clock(c: NewClock, user=Depends(current_user)):
    name = c.name.strip()

    if not name:
        raise HTTPException(400, "El nombre es obligatorio")

    now = time.time()
    cid = str(uuid.uuid4())[:8]

    with _lock:
        con = connect()
        con.execute(
            """
            INSERT INTO clocks(
                id, name, owner, status, started_at,
                elapsed_before_pause, created_at, updated_at
            ) VALUES (?, ?, ?, 'RUNNING', ?, 0, ?, ?)
            """,
            (cid, name, user["username"], now, now, now)
        )

        add_event(con, cid, "CREATED", user["username"])
        add_event(con, cid, "STARTED", user["username"])

        con.commit()

        row = con.execute(
            "SELECT * FROM clocks WHERE id = ?",
            (cid,)
        ).fetchone()

        con.close()

    result = serialize(row)
    await notify_change("CREATED", cid, user["username"])
    return result


@app.get("/clocks")
def list_clocks(user=Depends(current_user)):
    con = connect()

    if user["role"] == "ADMIN":
        rows = con.execute(
            "SELECT * FROM clocks ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = con.execute(
            """
            SELECT * FROM clocks
            WHERE owner = ?
            ORDER BY created_at DESC
            """,
            (user["username"],)
        ).fetchall()

    con.close()

    futures = [
        _executor.submit(serialize, row)
        for row in rows
    ]

    return [
        future.result()
        for future in futures
    ]



@app.post("/sync")
async def sync_clocks(payload: SyncClocks, user=Depends(current_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(403, "Solo ADMIN puede sincronizar relojes")

    ids = list(dict.fromkeys(payload.clock_ids))
    if len(ids) < 2:
        raise HTTPException(400, "Selecciona al menos dos relojes")

    now = time.time()

    with _lock:
        con = connect()
        placeholders = ",".join("?" for _ in ids)
        rows = con.execute(
            f"SELECT * FROM clocks WHERE id IN ({placeholders})",
            ids
        ).fetchall()

        if len(rows) != len(ids):
            con.close()
            raise HTTPException(404, "Uno o mas relojes no existen")

        for row in rows:
            con.execute(
                """
                UPDATE clocks
                SET status='RUNNING',
                    started_at=?,
                    elapsed_before_pause=0,
                    updated_at=?
                WHERE id=?
                """,
                (now, now, row["id"])
            )
            add_event(con, row["id"], "SYNCED", user["username"])

        con.commit()
        con.close()

    for row in rows:
        await notify_change("SYNCED", row["id"], row["owner"])

    return {
        "ok": True,
        "started_at": now,
        "clock_ids": ids
    }


@app.get("/clocks/{cid}")
def get_clock(cid: str, user=Depends(current_user)):
    row = get_clock_row(cid)
    require_access(row, user)
    return serialize(row)


@app.post("/clocks/{cid}/pause")
async def pause_clock(cid: str, user=Depends(current_user)):
    with _lock:
        row = get_clock_row(cid)
        require_access(row, user)

        if row["status"] != "RUNNING":
            raise HTTPException(
                409,
                "Solo se puede pausar un reloj en ejecucion"
            )

        elapsed = elapsed_for(row)
        now = time.time()

        con = connect()
        con.execute(
            """
            UPDATE clocks
            SET status='PAUSED',
                started_at=NULL,
                elapsed_before_pause=?,
                updated_at=?
            WHERE id=?
            """,
            (elapsed, now, cid)
        )

        add_event(con, cid, "PAUSED", user["username"])
        con.commit()

        updated = con.execute(
            "SELECT * FROM clocks WHERE id=?",
            (cid,)
        ).fetchone()

        con.close()

    result = serialize(updated)
    await notify_change("PAUSED", cid, updated["owner"])
    return result


@app.post("/clocks/{cid}/resume")
async def resume_clock(cid: str, user=Depends(current_user)):
    with _lock:
        row = get_clock_row(cid)
        require_access(row, user)

        if row["status"] != "PAUSED":
            raise HTTPException(
                409,
                "Solo se puede reanudar un reloj pausado"
            )

        now = time.time()

        con = connect()
        con.execute(
            """
            UPDATE clocks
            SET status='RUNNING',
                started_at=?,
                updated_at=?
            WHERE id=?
            """,
            (now, now, cid)
        )

        add_event(con, cid, "RESUMED", user["username"])
        con.commit()

        updated = con.execute(
            "SELECT * FROM clocks WHERE id=?",
            (cid,)
        ).fetchone()

        con.close()

    result = serialize(updated)
    await notify_change("RESUMED", cid, updated["owner"])
    return result


@app.post("/clocks/{cid}/stop")
async def stop_clock(cid: str, user=Depends(current_user)):
    with _lock:
        row = get_clock_row(cid)
        require_access(row, user)

        if row["status"] == "STOPPED":
            raise HTTPException(409, "El reloj ya esta detenido")

        elapsed = elapsed_for(row)
        now = time.time()

        con = connect()
        con.execute(
            """
            UPDATE clocks
            SET status='STOPPED',
                started_at=NULL,
                elapsed_before_pause=?,
                updated_at=?
            WHERE id=?
            """,
            (elapsed, now, cid)
        )

        add_event(con, cid, "STOPPED", user["username"])
        con.commit()

        updated = con.execute(
            "SELECT * FROM clocks WHERE id=?",
            (cid,)
        ).fetchone()

        con.close()

    result = serialize(updated)
    await notify_change("STOPPED", cid, updated["owner"])
    return result


@app.delete("/clocks/{cid}")
async def delete_clock(cid: str, user=Depends(current_user)):
    with _lock:
        row = get_clock_row(cid)
        require_access(row, user)
        owner = row["owner"]

        con = connect()

        add_event(
            con,
            cid,
            "DELETED",
            user["username"]
        )

        con.execute(
            "DELETE FROM clocks WHERE id = ?",
            (cid,)
        )

        con.commit()
        con.close()

    await notify_change("DELETED", cid, owner)
    return {"ok": True}


@app.get("/clocks/{cid}/history")
def clock_history(cid: str, user=Depends(current_user)):
    row = get_clock_row(cid)
    require_access(row, user)

    con = connect()

    rows = con.execute(
        """
        SELECT action, username, created_at
        FROM events
        WHERE clock_id=?
        ORDER BY id ASC
        """,
        (cid,)
    ).fetchall()

    con.close()

    return [
        dict(event)
        for event in rows
    ]

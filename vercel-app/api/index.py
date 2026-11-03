import os
import time
import uuid
from typing import Any

import bcrypt
import jwt
import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
ADMIN_USER = os.getenv("DEMO_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("DEMO_ADMIN_PASSWORD")

app = FastAPI(title="TimeControl XP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: list[WebSocket] = []


class Credentials(BaseModel):
    username: str
    password: str


class NewClock(BaseModel):
    name: str


def db():
    if not DATABASE_URL:
        raise HTTPException(500, "Falta DATABASE_URL")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def init_db():
    if not DATABASE_URL:
        return

    with db() as con:
        with con.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'USER'
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clocks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at DOUBLE PRECISION,
                    elapsed_before_pause DOUBLE PRECISION NOT NULL DEFAULT 0,
                    created_at DOUBLE PRECISION NOT NULL,
                    updated_at DOUBLE PRECISION NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id BIGSERIAL PRIMARY KEY,
                    clock_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    username TEXT NOT NULL,
                    created_at DOUBLE PRECISION NOT NULL
                )
            """)

            if ADMIN_PASSWORD:
                cur.execute(
                    "SELECT username FROM users WHERE username=%s",
                    (ADMIN_USER,)
                )
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO users(username,password_hash,role) VALUES (%s,%s,'ADMIN')",
                        (ADMIN_USER, hash_pw(ADMIN_PASSWORD))
                    )
        con.commit()


init_db()


def decode_token(token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token invalido")

    username = payload.get("sub")
    role = payload.get("role", "USER")

    if not username:
        raise HTTPException(401, "Token invalido")

    return {"username": username, "role": role}


def current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token requerido")
    return decode_token(authorization.split(" ", 1)[1])


def elapsed(clock: dict[str, Any]) -> float:
    value = float(clock.get("elapsed_before_pause") or 0)
    if clock["status"] == "RUNNING" and clock.get("started_at") is not None:
        value += time.time() - float(clock["started_at"])
    return max(0.0, value)


def serialize(clock: dict[str, Any]) -> dict[str, Any]:
    result = dict(clock)
    result["elapsed"] = elapsed(clock)
    return result


def get_clock(cid: str) -> dict[str, Any]:
    with db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM clocks WHERE id=%s", (cid,))
            row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Reloj no encontrado")
    return row


def require_access(clock: dict[str, Any], user: dict[str, str]):
    if user["role"] != "ADMIN" and clock["owner"] != user["username"]:
        raise HTTPException(403, "No tienes permiso para acceder a este reloj")


def add_event(cur, cid: str, action: str, username: str):
    cur.execute(
        "INSERT INTO events(clock_id,action,username,created_at) VALUES (%s,%s,%s,%s)",
        (cid, action, username, time.time())
    )


async def broadcast(action: str, clock_id: str, owner: str):
    payload = {
        "type": "clock_changed",
        "action": action,
        "clock_id": clock_id,
        "owner": owner,
        "timestamp": time.time()
    }

    dead = []
    for websocket in connections:
        try:
            await websocket.send_json(payload)
        except Exception:
            dead.append(websocket)

    for websocket in dead:
        if websocket in connections:
            connections.remove(websocket)


@app.get("/api/health")
def health():
    return {"ok": True, "websocket_clients": len(connections)}


@app.get("/api/time")
def server_time():
    return {"server_time_ms": time.time() * 1000}


@app.post("/api/register")
def register(c: Credentials):
    username = c.username.strip()
    password = c.password.strip()

    if len(username) < 3 or len(password) < 6:
        raise HTTPException(400, "Usuario o contraseña demasiado cortos")

    with db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE username=%s", (username,))
            if cur.fetchone():
                raise HTTPException(400, "El usuario ya existe")

            cur.execute(
                "INSERT INTO users(username,password_hash,role) VALUES (%s,%s,'USER')",
                (username, hash_pw(password))
            )
        con.commit()

    return {"ok": True}


@app.post("/api/login")
def login(c: Credentials):
    with db() as con:
        with con.cursor() as cur:
            cur.execute(
                "SELECT username,password_hash,role FROM users WHERE username=%s",
                (c.username.strip(),)
            )
            user = cur.fetchone()

    if not user or not verify_pw(c.password, user["password_hash"]):
        raise HTTPException(401, "Credenciales incorrectas")

    token = jwt.encode(
        {
            "sub": user["username"],
            "role": user["role"],
            "exp": int(time.time()) + 3600
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return {
        "token": token,
        "username": user["username"],
        "role": user["role"]
    }


@app.post("/api/clocks")
async def create_clock(c: NewClock, user=Depends(current_user)):
    name = c.name.strip()
    if not name:
        raise HTTPException(400, "El nombre es obligatorio")

    now = time.time()
    cid = str(uuid.uuid4())[:8]

    with db() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO clocks(
                    id,name,owner,status,started_at,
                    elapsed_before_pause,created_at,updated_at
                )
                VALUES (%s,%s,%s,'RUNNING',%s,0,%s,%s)
                """,
                (cid, name, user["username"], now, now, now)
            )
            add_event(cur, cid, "CREATED", user["username"])
            add_event(cur, cid, "STARTED", user["username"])
            cur.execute("SELECT * FROM clocks WHERE id=%s", (cid,))
            row = cur.fetchone()
        con.commit()

    await broadcast("CREATED", cid, user["username"])
    return serialize(row)


@app.get("/api/clocks")
def list_clocks(user=Depends(current_user)):
    with db() as con:
        with con.cursor() as cur:
            if user["role"] == "ADMIN":
                cur.execute("SELECT * FROM clocks ORDER BY created_at DESC")
            else:
                cur.execute(
                    "SELECT * FROM clocks WHERE owner=%s ORDER BY created_at DESC",
                    (user["username"],)
                )
            rows = cur.fetchall()

    return [serialize(row) for row in rows]


@app.get("/api/clocks/{cid}")
def read_clock(cid: str, user=Depends(current_user)):
    clock = get_clock(cid)
    require_access(clock, user)
    return serialize(clock)


@app.post("/api/clocks/{cid}/pause")
async def pause_clock(cid: str, user=Depends(current_user)):
    clock = get_clock(cid)
    require_access(clock, user)

    if clock["status"] != "RUNNING":
        raise HTTPException(409, "Solo se puede pausar un reloj en ejecución")

    value = elapsed(clock)
    now = time.time()

    with db() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                UPDATE clocks
                SET status='PAUSED', started_at=NULL,
                    elapsed_before_pause=%s, updated_at=%s
                WHERE id=%s
                """,
                (value, now, cid)
            )
            add_event(cur, cid, "PAUSED", user["username"])
        con.commit()

    await broadcast("PAUSED", cid, clock["owner"])
    return serialize(get_clock(cid))


@app.post("/api/clocks/{cid}/resume")
async def resume_clock(cid: str, user=Depends(current_user)):
    clock = get_clock(cid)
    require_access(clock, user)

    if clock["status"] != "PAUSED":
        raise HTTPException(409, "Solo se puede reanudar un reloj pausado")

    now = time.time()

    with db() as con:
        with con.cursor() as cur:
            cur.execute(
                "UPDATE clocks SET status='RUNNING', started_at=%s, updated_at=%s WHERE id=%s",
                (now, now, cid)
            )
            add_event(cur, cid, "RESUMED", user["username"])
        con.commit()

    await broadcast("RESUMED", cid, clock["owner"])
    return serialize(get_clock(cid))


@app.post("/api/clocks/{cid}/stop")
async def stop_clock(cid: str, user=Depends(current_user)):
    clock = get_clock(cid)
    require_access(clock, user)

    if clock["status"] == "STOPPED":
        raise HTTPException(409, "El reloj ya está detenido")

    value = elapsed(clock)
    now = time.time()

    with db() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                UPDATE clocks
                SET status='STOPPED', started_at=NULL,
                    elapsed_before_pause=%s, updated_at=%s
                WHERE id=%s
                """,
                (value, now, cid)
            )
            add_event(cur, cid, "STOPPED", user["username"])
        con.commit()

    await broadcast("STOPPED", cid, clock["owner"])
    return serialize(get_clock(cid))


@app.delete("/api/clocks/{cid}")
async def delete_clock(cid: str, user=Depends(current_user)):
    clock = get_clock(cid)
    require_access(clock, user)

    with db() as con:
        with con.cursor() as cur:
            add_event(cur, cid, "DELETED", user["username"])
            cur.execute("DELETE FROM clocks WHERE id=%s", (cid,))
        con.commit()

    await broadcast("DELETED", cid, clock["owner"])
    return {"ok": True}


@app.get("/api/clocks/{cid}/history")
def history(cid: str, user=Depends(current_user)):
    clock = get_clock(cid)
    require_access(clock, user)

    with db() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                SELECT action,username,created_at
                FROM events
                WHERE clock_id=%s
                ORDER BY id ASC
                """,
                (cid,)
            )
            rows = cur.fetchall()

    return rows


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        decode_token(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)

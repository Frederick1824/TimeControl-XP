import os, sqlite3, hashlib, time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt

DB = "/data/users.db"
SECRET = os.getenv("JWT_SECRET", "dev-secret")

app = FastAPI(title="auth-svc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'USER'
    )""")
    # usuario admin de prueba
    try:
        con.execute("INSERT INTO users VALUES (?, ?, ?)",
                    ("admin", hashlib.sha256(b"admin123").hexdigest(), "ADMIN"))
    except sqlite3.IntegrityError:
        pass
    con.commit()
    con.close()

init_db()

class Credentials(BaseModel):
    username: str
    password: str

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

@app.post("/register")
def register(c: Credentials):
    con = sqlite3.connect(DB)
    try:
        con.execute("INSERT INTO users VALUES (?, ?, ?)",
                    (c.username, hash_pw(c.password), "USER"))
        con.commit()
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(400, "El usuario ya existe")
    con.close()
    return {"ok": True}

@app.post("/login")
def login(c: Credentials):
    con = sqlite3.connect(DB)
    row = con.execute("SELECT password_hash, role FROM users WHERE username=?",
                      (c.username,)).fetchone()
    con.close()
    if not row or row[0] != hash_pw(c.password):
        raise HTTPException(401, "Credenciales incorrectas")
    token = jwt.encode(
        {"sub": c.username, "role": row[1], "exp": int(time.time()) + 3600},
        SECRET, algorithm="HS256")
    return {"token": token, "username": c.username, "role": row[1]}

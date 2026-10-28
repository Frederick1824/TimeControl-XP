import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="clock-svc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# En memoria: id -> started_at (epoch seconds). Nada de acumuladores.
_clocks: dict[str, float] = {}

class NewClock(BaseModel):
    name: str
    owner: str

@app.post("/clocks")
def create_clock(c: NewClock):
    import uuid
    cid = str(uuid.uuid4())[:8]
    _clocks[cid] = time.time()
    return {"id": cid, "name": c.name, "owner": c.owner,
            "started_at": _clocks[cid]}

@app.get("/clocks/{cid}")
def get_clock(cid: str):
    if cid not in _clocks:
        return {"error": "not found"}, 404
    return {
        "id": cid,
        "started_at": _clocks[cid],
        "elapsed": time.time() - _clocks[cid],
        # el cliente calcula: now() - started_at
    }

@app.delete("/clocks/{cid}")
def delete_clock(cid: str):
    _clocks.pop(cid, None)
    return {"ok": True}

@app.get("/clocks")
def list_clocks():
    now = time.time()
    return [{"id": k, "started_at": v, "elapsed": now - v} for k, v in _clocks.items()]

import os
import uuid

import redis
from fastapi import FastAPI, HTTPException
from redis.exceptions import RedisError

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    socket_connect_timeout=5,
    socket_timeout=5,
)


@app.get("/healthz")
def healthcheck():
    try:
        r.ping()
    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="redis unavailable",
        ) from exc
    return {"status": "ok"}


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        return {"error": "not found"}
    return {"job_id": job_id, "status": status.decode()}

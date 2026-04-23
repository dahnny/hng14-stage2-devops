import os
import time
from pathlib import Path

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_RETRY_DELAY_SECONDS = int(os.getenv("REDIS_RETRY_DELAY_SECONDS", "5"))
HEARTBEAT_FILE = Path(
    os.getenv("WORKER_HEARTBEAT_FILE", "/tmp/worker-heartbeat")
)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=5)


def update_heartbeat():
    HEARTBEAT_FILE.touch()


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


while True:
    try:
        r.ping()
        update_heartbeat()

        job = r.brpop("job", timeout=5)
        update_heartbeat()

        if job:
            _, job_id = job
            process_job(job_id.decode())
            update_heartbeat()
    except redis.exceptions.RedisError as exc:
        print(f"Redis unavailable: {exc}")
        time.sleep(REDIS_RETRY_DELAY_SECONDS)

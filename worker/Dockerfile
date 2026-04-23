FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV"

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    WORKER_HEARTBEAT_FILE=/tmp/worker-heartbeat \
    WORKER_HEALTH_TTL_SECONDS=30

WORKDIR /app

RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --create-home appuser

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup worker.py ./worker.py

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import os, sys, time; from pathlib import Path; path = Path(os.getenv('WORKER_HEARTBEAT_FILE', '/tmp/worker-heartbeat')); ttl = int(os.getenv('WORKER_HEALTH_TTL_SECONDS', '30')); healthy = path.exists() and (time.time() - path.stat().st_mtime) < ttl; sys.exit(0 if healthy else 1)"]

CMD ["python", "worker.py"]
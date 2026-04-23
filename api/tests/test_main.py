import importlib.util
import uuid
from pathlib import Path

import pytest
from fastapi import HTTPException
from redis.exceptions import RedisError


class FakeRedis:
    def __init__(self):
        self.jobs = []
        self.statuses = {}
        self.should_fail_ping = False

    def ping(self):
        if self.should_fail_ping:
            raise RedisError("redis unavailable")
        return True

    def lpush(self, name, value):
        self.jobs.insert(0, (name, value))

    def hset(self, key, field, value):
        self.statuses.setdefault(key, {})[field] = value

    def hget(self, key, field):
        value = self.statuses.get(key, {}).get(field)
        if value is None:
            return None
        return str(value).encode()


@pytest.fixture
def api_module(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "redis-internal")
    monkeypatch.setenv("REDIS_PORT", "6379")

    main_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("main_under_test", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)

    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "r", fake_redis)

    return module, fake_redis


def test_healthcheck_returns_ok_when_redis_is_available(api_module):
    module, _ = api_module

    assert module.healthcheck() == {"status": "ok"}


def test_healthcheck_returns_503_when_redis_is_unavailable(api_module):
    module, fake_redis = api_module
    fake_redis.should_fail_ping = True

    with pytest.raises(HTTPException) as exc_info:
        module.healthcheck()

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "redis unavailable"


def test_create_job_enqueues_job_and_marks_it_queued(api_module):
    module, fake_redis = api_module

    response = module.create_job()
    job_id = response["job_id"]

    assert str(uuid.UUID(job_id)) == job_id
    assert fake_redis.jobs == [("job", job_id)]
    assert fake_redis.statuses[f"job:{job_id}"]["status"] == "queued"


def test_get_job_returns_job_status_when_present(api_module):
    module, fake_redis = api_module
    fake_redis.hset("job:job-123", "status", "completed")

    assert module.get_job("job-123") == {
        "job_id": "job-123",
        "status": "completed",
    }


def test_get_job_returns_not_found_for_missing_job(api_module):
    module, _ = api_module

    assert module.get_job("missing-job") == {"error": "not found"}

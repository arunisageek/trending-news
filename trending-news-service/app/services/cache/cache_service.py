from __future__ import annotations

import json
import time
from threading import Lock
from typing import Any

import redis
from redis.exceptions import RedisError

from app.core.config import get_settings


class InMemoryTTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None

            expires_at, value = item
            if expires_at < time.time():
                self._store.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = (time.time() + ttl_seconds, value)

    def delete_by_prefix(self, prefix: str) -> None:
        with self._lock:
            keys = [key for key in self._store.keys() if key.startswith(prefix)]
            for key in keys:
                self._store.pop(key, None)


class CacheService:
    def __init__(self) -> None:
        settings = get_settings()
        self.redis_client = None
        self.memory_cache = InMemoryTTLCache()
        if settings.redis_url:
            try:
                self.redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
                self.redis_client.ping()
            except RedisError:
                self.redis_client = None

    def get(self, key: str) -> Any | None:
        if self.redis_client:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        return self.memory_cache.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if self.redis_client:
            self.redis_client.setex(key, ttl_seconds, json.dumps(value))
            return
        self.memory_cache.set(key, value, ttl_seconds)

    def invalidate_bucket(self, bucket_id: str) -> None:
        prefix = f"trending:bucket:{bucket_id}:"
        if self.redis_client:
            for key in self.redis_client.scan_iter(match=f"{prefix}*"):
                self.redis_client.delete(key)
            return
        self.memory_cache.delete_by_prefix(prefix)

    def feed_cache_key(self, bucket_id: str, limit: int, radius_km: float) -> str:
        return f"trending:bucket:{bucket_id}:limit:{limit}:radius:{round(radius_km, 2)}"


cache_service = CacheService()

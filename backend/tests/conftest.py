"""Pytest fixtures for PT Coach backend tests."""
import sys, os, json
import pytest

# Ensure backend/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_redis(monkeypatch):
    """Replace the redis module-level client with a dict-backed mock."""
    import redis_client as rc

    store = {}
    hstore = {}
    cache_store = {}
    lists = {}

    def fake_hset(session_id, field, value):
        hstore.setdefault(session_id, {})[field] = value

    def fake_hget(session_id, field):
        return hstore.get(session_id, {}).get(field)

    def fake_push_frame(session_id, payload):
        lists.setdefault(session_id, []).insert(0, json.dumps(payload))

    def fake_get_frames(session_id, limit=60):
        return [json.loads(f) for f in lists.get(session_id, [])[:limit]]

    def fake_set_cache(key, value, ex):
        cache_store[key] = value

    def fake_get_cache(key):
        return cache_store.get(key)

    monkeypatch.setattr(rc, 'hset',       fake_hset)
    monkeypatch.setattr(rc, 'hget',       fake_hget)
    monkeypatch.setattr(rc, 'push_frame', fake_push_frame)
    monkeypatch.setattr(rc, 'get_frames', fake_get_frames)
    monkeypatch.setattr(rc, 'set_cache',  fake_set_cache)
    monkeypatch.setattr(rc, 'get_cache',  fake_get_cache)

    return hstore


@pytest.fixture
def client(mock_redis):
    """Flask test client with Redis mocked out."""
    import app as app_module
    app_module.app.config['TESTING'] = True
    with app_module.app.test_client() as c:
        yield c

import json
import redis
from config import Config

r = redis.from_url(Config.REDIS_URL, decode_responses=True)

def push_frame(session_id, payload):
    key = f"session:{session_id}:frames"
    r.lpush(key, json.dumps(payload))
    r.ltrim(key, 0, Config.SESSION_FRAME_CAP - 1)

def get_frames(session_id, limit=60):
    key = f"session:{session_id}:frames"
    items = r.lrange(key, 0, limit - 1)
    return [json.loads(i) for i in items]

def hset(session_id, field, value):
    key = f"session:{session_id}:metrics"
    r.hset(key, field, json.dumps(value))

def hget(session_id, field):
    key = f"session:{session_id}:metrics"
    val = r.hget(key, field)
    if not val:
        return None
    return json.loads(val)

def incr(session_id, field):
    key = f"session:{session_id}:counters"
    return r.hincrby(key, field, 1)

def set_cache(key, value, ex):
    r.set(key, json.dumps(value), ex=ex)

def get_cache(key):
    val = r.get(key)
    if not val:
        return None
    return json.loads(val)

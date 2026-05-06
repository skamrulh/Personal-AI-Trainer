"""
PT Coach — Flask backend API
"""
import uuid
import time
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import Config
from redis_client import push_frame, get_frames, hset, hget
from form_analysis import compute_squat_metrics, detect_squat_faults
from openai_client import call_llm, build_feedback_prompt

LOG = logging.getLogger("app")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/v1/session/start', methods=['POST'])
def start_session():
    body = request.json or {}
    session_id = str(uuid.uuid4())
    meta = {
        "started_at": time.time(),
        "exercise":   body.get("exercise", "squat"),
        "user_id":    body.get("user_id",  "anon"),
    }
    hset(session_id, "meta",             meta)
    hset(session_id, "reps",             0)
    hset(session_id, "last_warning",     [])
    hset(session_id, "last_warning_prev", [])
    return jsonify({"session_id": session_id})


@app.route('/api/v1/session/<session_id>/frame', methods=['POST'])
def frame(session_id):
    payload = request.json
    if not payload or 'keypoints' not in payload:
        return jsonify({"error": "invalid payload"}), 400

    payload['received_at'] = time.time()
    push_frame(session_id, payload)

    metrics  = compute_squat_metrics(payload['keypoints'])
    warnings = detect_squat_faults(metrics)

    hset(session_id, "latest_metrics", metrics)
    hset(session_id, "last_warning",   warnings)

    short = "; ".join(warnings) if warnings else None
    long_msg = None

    prev = hget(session_id, "last_warning_prev") or []
    if warnings and warnings != prev:
        # FIX 4: safe meta access — hget can return None if session expired
        meta     = hget(session_id, "meta") or {}
        exercise = meta.get("exercise", "squat")
        prompt   = build_feedback_prompt(exercise, warnings, metrics)
        try:
            resp     = call_llm(prompt)
            long_msg = resp.get("text")
            hset(session_id, "last_llm", resp)
        except Exception as exc:
            LOG.warning("LLM call failed: %s", exc)
            long_msg = None

    hset(session_id, "last_warning_prev", warnings)

    return jsonify({
        "ok":      True,
        "warnings": warnings,
        "short":    short,
        "long":     long_msg,
        "metrics":  metrics,
    })


@app.route('/api/v1/session/<session_id>/metrics', methods=['GET'])
def get_metrics(session_id):
    meta         = hget(session_id, "meta")
    latest       = hget(session_id, "latest_metrics")
    last_warning = hget(session_id, "last_warning")
    return jsonify({
        "meta":            meta,
        "latest_metrics":  latest,
        "last_warning":    last_warning,
    })


@app.route('/api/v1/session/<session_id>/chat', methods=['POST'])
def chat(session_id):
    body = request.json or {}
    text = body.get("text")
    if not text:
        return jsonify({"error": "no text"}), 400

    # FIX 4: safe meta/metrics access throughout
    meta     = hget(session_id, "meta")     or {}
    metrics  = hget(session_id, "latest_metrics") or {}
    warnings = hget(session_id, "last_warning")   or []

    exercise = meta.get("exercise", "squat")
    prompt   = build_feedback_prompt(exercise, warnings, metrics)
    prompt["messages"].append({"role": "user", "content": text})

    try:
        resp = call_llm(prompt)
        return jsonify({"reply": resp.get("text")})
    except Exception as exc:
        LOG.error("LLM error in /chat: %s", exc)
        return jsonify({"error": "LLM error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)

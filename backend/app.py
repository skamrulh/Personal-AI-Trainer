from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid, time
from config import Config
from redis_client import push_frame, get_frames, hset, hget
from form_analysis import compute_squat_metrics, detect_squat_faults
from openai_client import call_llm, build_feedback_prompt

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'})

@app.route('/api/v1/session/start', methods=['POST'])
def start_session():
    body = request.json or {}
    session_id = str(uuid.uuid4())
    meta = {
        "started_at": time.time(),
        "exercise": body.get("exercise", "squat"),
        "user_id": body.get("user_id", "anon")
    }
    hset(session_id, "meta", meta)
    hset(session_id, "reps", 0)
    hset(session_id, "last_warning", [])
    return jsonify({"session_id": session_id})

@app.route('/api/v1/session/<session_id>/frame', methods=['POST'])
def frame(session_id):
    payload = request.json
    if not payload or 'keypoints' not in payload:
        return jsonify({"error": "invalid payload"}), 400
    payload['received_at'] = time.time()
    push_frame(session_id, payload)
    metrics = compute_squat_metrics(payload['keypoints'])
    warnings = detect_squat_faults(metrics)
    # update session metrics
    hset(session_id, "latest_metrics", metrics)
    hset(session_id, "last_warning", warnings)
    # quick templated feedback
    short = "; ".join(warnings) if warnings else None
    long = None
    # call LLM only if new warnings
    prev = hget(session_id, "last_warning_prev") or []
    if warnings and warnings != prev:
        prompt = build_feedback_prompt(hget(session_id,"meta")['exercise'], warnings, metrics)
        try:
            resp = call_llm(prompt)
            long = resp.get("text")
            hset(session_id, "last_llm", resp)
        except Exception as e:
            long = None
    hset(session_id, "last_warning_prev", warnings)
    return jsonify({"ok": True, "warnings": warnings, "short": short, "long": long, "metrics": metrics})

@app.route('/api/v1/session/<session_id>/metrics', methods=['GET'])
def metrics(session_id):
    meta = hget(session_id, "meta")
    latest = hget(session_id, "latest_metrics")
    last_warning = hget(session_id, "last_warning")
    return jsonify({"meta": meta, "latest_metrics": latest, "last_warning": last_warning})

@app.route('/api/v1/session/<session_id>/chat', methods=['POST'])
def chat(session_id):
    body = request.json or {}
    text = body.get("text")
    if not text:
        return jsonify({"error":"no text"}), 400
    meta = hget(session_id, "meta") or {}
    metrics = hget(session_id, "latest_metrics") or {}
    warnings = hget(session_id, "last_warning") or []
    prompt = build_feedback_prompt(meta.get('exercise','squat'), warnings, metrics)
    # append user question
    prompt['messages'].append({"role":"user","content": text})
    try:
        resp = call_llm(prompt)
        return jsonify({"reply": resp.get("text")})
    except Exception:
        return jsonify({"error":"LLM error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)

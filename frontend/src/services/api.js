import axios from 'axios';
const BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

export async function startSession(exercise='squat'){
  const r = await axios.post(`${BASE}/api/v1/session/start`, { exercise });
  return r.data.session_id;
}

export async function sendFrame(sessionId, keypoints){
  const payload = { ts: Date.now(), keypoints };
  const r = await axios.post(`${BASE}/api/v1/session/${sessionId}/frame`, payload);
  return r.data;
}

export async function getMetrics(sessionId){
  const r = await axios.get(`${BASE}/api/v1/session/${sessionId}/metrics`);
  return r.data;
}

export async function sessionChat(sessionId, text){
  const r = await axios.post(`${BASE}/api/v1/session/${sessionId}/chat`, { text });
  return r.data;
}

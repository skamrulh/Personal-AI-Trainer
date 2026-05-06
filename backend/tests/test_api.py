"""Tests for Flask API endpoints (app.py)."""
import json
import pytest


class TestHealth:
    def test_health_returns_200(self, client):
        r = client.get('/health')
        assert r.status_code == 200
        assert r.get_json()['status'] == 'ok'


class TestStartSession:
    def test_returns_session_id(self, client):
        r = client.post('/api/v1/session/start',
                        data=json.dumps({}),
                        content_type='application/json')
        assert r.status_code == 200
        data = r.get_json()
        assert 'session_id' in data
        assert len(data['session_id']) > 0

    def test_custom_exercise(self, client):
        r = client.post('/api/v1/session/start',
                        data=json.dumps({'exercise': 'lunge'}),
                        content_type='application/json')
        assert r.status_code == 200

    def test_multiple_sessions_have_unique_ids(self, client):
        r1 = client.post('/api/v1/session/start',
                         data=json.dumps({}),
                         content_type='application/json').get_json()
        r2 = client.post('/api/v1/session/start',
                         data=json.dumps({}),
                         content_type='application/json').get_json()
        assert r1['session_id'] != r2['session_id']


class TestFrameEndpoint:
    def _start(self, client):
        r = client.post('/api/v1/session/start',
                        data=json.dumps({'exercise': 'squat'}),
                        content_type='application/json')
        return r.get_json()['session_id']

    def _kps(self):
        """Minimal valid keypoints for a standing squat pose."""
        names = ['left_hip', 'left_knee', 'left_ankle',
                 'right_hip', 'right_knee', 'right_ankle']
        return [{'name': n, 'x': i * 10, 'y': i * 5, 'score': 0.9}
                for i, n in enumerate(names)]

    def test_valid_frame_returns_ok(self, client):
        sid = self._start(client)
        r = client.post(f'/api/v1/session/{sid}/frame',
                        data=json.dumps({'keypoints': self._kps()}),
                        content_type='application/json')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert 'warnings' in data
        assert 'metrics'  in data

    def test_missing_keypoints_returns_400(self, client):
        sid = self._start(client)
        r = client.post(f'/api/v1/session/{sid}/frame',
                        data=json.dumps({'bad': 'payload'}),
                        content_type='application/json')
        assert r.status_code == 400

    def test_empty_body_returns_400(self, client):
        sid = self._start(client)
        r = client.post(f'/api/v1/session/{sid}/frame',
                        data='',
                        content_type='application/json')
        assert r.status_code == 400

    def test_session_not_initialised_does_not_crash(self, client):
        """FIX 4 regression: hget returning None must not crash the endpoint."""
        r = client.post('/api/v1/session/nonexistent-uuid/frame',
                        data=json.dumps({'keypoints': self._kps()}),
                        content_type='application/json')
        # Should return 200 (best-effort) not 500
        assert r.status_code == 200


class TestMetricsEndpoint:
    def test_returns_meta_and_metrics(self, client):
        r = client.post('/api/v1/session/start',
                        data=json.dumps({}), content_type='application/json')
        sid = r.get_json()['session_id']

        r2 = client.get(f'/api/v1/session/{sid}/metrics')
        assert r2.status_code == 200
        data = r2.get_json()
        assert 'meta'           in data
        assert 'latest_metrics' in data
        assert 'last_warning'   in data


class TestChatEndpoint:
    def test_no_text_returns_400(self, client):
        r = client.post('/api/v1/session/start',
                        data=json.dumps({}), content_type='application/json')
        sid = r.get_json()['session_id']
        r2 = client.post(f'/api/v1/session/{sid}/chat',
                         data=json.dumps({}), content_type='application/json')
        assert r2.status_code == 400

    def test_llm_error_returns_500(self, client, monkeypatch):
        import openai_client
        monkeypatch.setattr(openai_client, 'call_llm',
                            lambda _: (_ for _ in ()).throw(RuntimeError("LLM down")))
        r = client.post('/api/v1/session/start',
                        data=json.dumps({}), content_type='application/json')
        sid = r.get_json()['session_id']
        r2 = client.post(f'/api/v1/session/{sid}/chat',
                         data=json.dumps({'text': 'help'}),
                         content_type='application/json')
        assert r2.status_code == 500


class TestOpenaiClient:
    def test_build_feedback_prompt_has_messages(self):
        from openai_client import build_feedback_prompt
        prompt = build_feedback_prompt('squat', ['left_knee_bend_too_far'], {'left_knee': 60})
        assert 'messages' in prompt
        assert len(prompt['messages']) == 2
        assert prompt['messages'][0]['role'] == 'system'
        assert prompt['messages'][1]['role'] == 'user'

    def test_build_feedback_prompt_contains_exercise(self):
        from openai_client import build_feedback_prompt
        prompt = build_feedback_prompt('deadlift', [], {})
        assert 'deadlift' in prompt['messages'][1]['content']

    def test_call_llm_uses_cache(self, monkeypatch):
        import openai_client, redis_client
        cached_result = {'text': 'cached response'}
        monkeypatch.setattr(openai_client, "get_cache", lambda _: cached_result)
        # If cache hits, the OpenAI client should NOT be called
        called = []
        monkeypatch.setattr(openai_client, '_client', type('C', (), {
            'chat': type('Ch', (), {
                'completions': type('Co', (), {
                    'create': lambda *a, **kw: called.append(True)
                })()
            })()
        })())
        result = openai_client.call_llm({'messages': []})
        assert result == cached_result
        assert called == []  # API was NOT called


class TestRedisClient:
    def test_hset_hget_roundtrip(self, mock_redis):
        import redis_client as rc
        rc.hset('sess1', 'key1', {'foo': 'bar'})
        assert rc.hget('sess1', 'key1') == {'foo': 'bar'}

    def test_hget_missing_returns_none(self, mock_redis):
        import redis_client as rc
        assert rc.hget('does-not-exist', 'field') is None

    def test_push_and_get_frames(self, mock_redis):
        import redis_client as rc
        rc.push_frame('s1', {'keypoints': []})
        frames = rc.get_frames('s1')
        assert len(frames) == 1
        assert frames[0] == {'keypoints': []}

    def test_set_and_get_cache(self, mock_redis):
        import redis_client as rc
        rc.set_cache('llm_cache:abc', {'text': 'hi'}, ex=30)
        assert rc.get_cache('llm_cache:abc') == {'text': 'hi'}

    def test_get_cache_miss_returns_none(self, mock_redis):
        import redis_client as rc
        assert rc.get_cache('nonexistent') is None

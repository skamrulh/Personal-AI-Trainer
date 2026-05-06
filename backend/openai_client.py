"""
openai_client.py — LLM interface for PT Coach backend.

Upgraded from openai==0.27.8 (v0 API) to openai>=1.0.0 (v1 API).
Key API change: openai.ChatCompletion.create() → client.chat.completions.create()
"""
import json
import hashlib

from openai import OpenAI
from tenacity import retry, wait_exponential, stop_after_attempt

from config import Config
from redis_client import get_cache, set_cache

# FIX 3: Use v1 client instead of module-level api_key assignment
_client = OpenAI(api_key=Config.OPENAI_API_KEY)


def _cache_key(prompt_obj: dict) -> str:
    s = json.dumps(prompt_obj, sort_keys=True)
    return "llm_cache:" + hashlib.sha256(s.encode()).hexdigest()


@retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
def call_llm(prompt_obj: dict) -> dict:
    """
    Call the OpenAI chat API with Redis caching.

    Args:
        prompt_obj: dict with a 'messages' key containing the chat history,
                    as produced by build_feedback_prompt().

    Returns:
        dict with key 'text' containing the model's reply.
    """
    cache_key = _cache_key(prompt_obj)
    cached = get_cache(cache_key)
    if cached:
        return cached

    # FIX 15: removed the unreachable system/user fallback branch —
    # build_feedback_prompt always produces {"messages": [...]}.
    messages = prompt_obj.get("messages", [])

    # FIX 3: Use openai v1 client API
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=300,
        temperature=0.3,
    )
    text = response.choices[0].message.content
    result = {"text": text}

    set_cache(cache_key, result, ex=Config.LLM_CACHE_TTL)
    return result


def build_feedback_prompt(exercise_name: str, warnings: list, summary: dict) -> dict:
    """
    Build the messages list for a form-feedback LLM call.

    Returns a dict with key 'messages' ready for call_llm() or direct appending
    (used by the /chat endpoint).
    """
    system = (
        "You are a professional physical therapist and form coach. "
        "Given the exercise, detected warnings (short labels), and numeric summary "
        "produce a JSON object with keys: short (<=20 chars), long (<=120 chars), "
        "tone (encouraging|firm). "
        "If warnings include 'pain', return short: 'Stop — consult a professional.'"
    )
    user = (
        f"Exercise: {exercise_name}\n"
        f"Warnings: {warnings}\n"
        f"Summary: {summary}\n"
        f"Return plain JSON object only."
    )
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ]
    }

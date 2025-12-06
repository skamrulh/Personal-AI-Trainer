import openai, json, hashlib
from config import Config
from redis_client import get_cache, set_cache
from tenacity import retry, wait_exponential, stop_after_attempt

openai.api_key = Config.OPENAI_API_KEY

def _cache_key(prompt_obj):
    s = json.dumps(prompt_obj, sort_keys=True)
    return "llm_cache:" + hashlib.sha256(s.encode()).hexdigest()

@retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
def call_llm(prompt_obj):
    """
    prompt_obj: {system: str, user: str} or messages list under 'messages'
    returns: dict {text:...}
    """
    cache_key = _cache_key(prompt_obj)
    c = get_cache(cache_key)
    if c:
        return c
    messages = prompt_obj.get('messages')
    if not messages:
        messages = [
            {"role": "system", "content": prompt_obj.get("system", "You are an expert PT coach.")},
            {"role": "user", "content": prompt_obj.get("user", "")}
        ]
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=300,
        temperature=0.3
    )
    text = resp['choices'][0]['message']['content']
    result = {"text": text}
    set_cache(cache_key, result, ex=Config.LLM_CACHE_TTL)
    return result

def build_feedback_prompt(exercise_name, warnings, summary):
    system = ("You are a professional physical therapist and form coach. "
              "Given the exercise, detected warnings (short labels), and numeric summary produce a JSON with keys: short (<=20 chars), long (<=120 chars), tone (encouraging|firm). If warnings include 'pain', return short: 'Stop — consult a professional.'")
    user = f"Exercise: {exercise_name}\nWarnings: {warnings}\nSummary: {summary}\nReturn plain JSON object."
    return {"messages": [{"role":"system","content":system},{"role":"user","content":user}]}

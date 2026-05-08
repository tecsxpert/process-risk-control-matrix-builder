import os
import json
import hashlib
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

try:
    import redis as redis_lib
    redis_client = redis_lib.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)
    redis_client.ping()
    REDIS_AVAILABLE = True
    print("Redis connected")
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False
    print("Redis not available — cache disabled")

FALLBACK_TEMPLATES = {
    "describe": {
        "process_description": "Unable to generate description at this time",
        "risks": ["Service unavailable"],
        "controls": ["Please try again later"],
        "is_fallback": True
    },
    "recommend": [
        {"action_type": "Preventive", "description": "Service unavailable — please retry", "priority": "High"}
    ],
    "report": {
        "title": "Report Unavailable",
        "summary": "AI service temporarily unavailable",
        "overview": "Please try again later",
        "key_items": ["Service unavailable"],
        "recommendations": ["Retry when service is restored"],
        "is_fallback": True
    }
}

def call_groq(prompt_type, user_input, context: str = ""):
    from prompts.loader import load_prompt

    prompt = load_prompt(f"{prompt_type}.txt").replace("{input}", user_input)

    if context:
        prompt = f"""Use the following reference context to assist your response:

--- CONTEXT START ---
{context}
--- CONTEXT END ---

{prompt}"""

    cache_key = "ai:" + hashlib.sha256(prompt.encode()).hexdigest()
    if REDIS_AVAILABLE:
        cached = redis_client.get(cache_key)
        if cached:
            print("Cache hit!")
            return json.loads(cached)

    for attempt in range(3):
        try:
            start = time.time()
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=10
            )
            elapsed = round((time.time() - start) * 1000)
            print(f"Groq response time: {elapsed}ms")

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                result = json.loads(content)

                if REDIS_AVAILABLE:
                    redis_client.setex(cache_key, 900, json.dumps(result))

                return result

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    return FALLBACK_TEMPLATES.get(prompt_type, {"is_fallback": True, "message": "AI service temporarily unavailable"})
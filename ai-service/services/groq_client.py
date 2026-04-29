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
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False

def call_groq(prompt_type, user_input):
    from prompts.loader import load_prompt

    prompt = load_prompt(f"{prompt_type}.txt").replace("{input}", user_input)

    cache_key = "ai:" + hashlib.sha256(prompt.encode()).hexdigest()
    if REDIS_AVAILABLE:
        cached = redis_client.get(cache_key)
        if cached:
            print("Cache hit!")
            return json.loads(cached)

    for attempt in range(3):
        try:
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

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                result = json.loads(content)

                if REDIS_AVAILABLE:
                    redis_client.setex(cache_key, 900, json.dumps(result))

                return result

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    return {"is_fallback": True, "message": "AI service temporarily unavailable"}
import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

def call_groq(prompt_type, user_input):
    from prompts.loader import load_prompt

    prompt = load_prompt(f"{prompt_type}.txt").replace("{input}", user_input)

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
                return json.loads(content)

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    return {"is_fallback": True, "message": "AI service temporarily unavailable"}
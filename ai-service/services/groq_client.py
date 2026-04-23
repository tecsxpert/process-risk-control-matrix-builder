import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

def call_groq(prompt_type, user_input):
    for attempt in range(3):
        try:
            # Load prompt
            with open(f"prompts/{prompt_type}.txt", "r") as f:
                prompt = f.read().replace("{input}", user_input)

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)

        time.sleep(2 ** attempt)

    return None
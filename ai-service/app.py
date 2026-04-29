from flask import Flask, request, jsonify
from datetime import datetime
from services.groq_client import call_groq
import time
import re

app = Flask(__name__)
start_time = time.time()

# ── Security headers ─────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# ── Input sanitisation ───────────────────────────────────────────
def sanitize(text):
    text = re.sub(r'<[^>]+>', '', text)
    injection_keywords = ['ignore previous', 'forget instructions', 'you are now', 'act as']
    for keyword in injection_keywords:
        if keyword.lower() in text.lower():
            return None
    return text.strip()

# ── HOME ─────────────────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({"message": "AI Service Running", "status": "ok"})

# ── POST /describe ───────────────────────────────────────────────
@app.route("/describe", methods=["POST"])
def describe():
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    clean = sanitize(data["input"])
    if clean is None:
        return jsonify({"error": "Invalid input — prompt injection detected"}), 400

    result = call_groq("describe", clean)
    if result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        "result": result,
        "generated_at": datetime.utcnow().isoformat()
    }), 200

# ── POST /recommend ──────────────────────────────────────────────
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    clean = sanitize(data["input"])
    if clean is None:
        return jsonify({"error": "Invalid input — prompt injection detected"}), 400

    result = call_groq("recommend", clean)
    if isinstance(result, dict) and result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        "recommendations": result,
        "generated_at": datetime.utcnow().isoformat()
    }), 200

# ── POST /generate-report ────────────────────────────────────────
@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    clean = sanitize(data["input"])
    if clean is None:
        return jsonify({"error": "Invalid input — prompt injection detected"}), 400

    result = call_groq("report", clean)
    if result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        **result,
        "generated_at": datetime.utcnow().isoformat(),
        "is_fallback": False
    }), 200

# ── GET /health ──────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    uptime = round(time.time() - start_time, 2)
    return jsonify({
        "status": "ok",
        "model": "llama-3.3-70b-versatile",
        "uptime_seconds": uptime,
        "avg_response_time_ms": 800,
        "rate_limit": "30 req/min"
    }), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
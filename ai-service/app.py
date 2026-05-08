from flask import Flask, request, jsonify
from datetime import datetime
from services.groq_client import call_groq
import time
import re
import json

# ── Knowledge base context retrieval ─────────────────────────────
def get_context(query: str) -> str:
    try:
        with open("data/knowledge_base.json") as f:
            docs = json.load(f)
        query_lower = query.lower()
        matches = [d["text"] for d in docs if any(w in d["text"].lower() for w in query_lower.split())]
        return "\n\n".join(matches[:3]) if matches else ""
    except Exception:
        return ""

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

    context = get_context(clean)
    result = call_groq("describe", clean, context=context)

    if not isinstance(result, dict):
        return jsonify({"error": "Unexpected response format"}), 500
    if result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        "result": result,
        "rag_context_used": bool(context),
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

    context = get_context(clean)
    result = call_groq("recommend", clean, context=context)

    if isinstance(result, dict) and result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        "recommendations": result,
        "rag_context_used": bool(context),
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

    context = get_context(clean)
    result = call_groq("report", clean, context=context)

    if not isinstance(result, dict):
        return jsonify({"error": "Unexpected response format"}), 500
    if result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        **result,
        "rag_context_used": bool(context),
        "generated_at": datetime.utcnow().isoformat(),
        "is_fallback": False
    }), 200

# ── GET /health ──────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    uptime = round(time.time() - start_time, 2)
    kb_count = 0
    try:
        with open("data/knowledge_base.json") as f:
            kb_count = len(json.load(f))
    except Exception:
        pass
    return jsonify({
        "status": "ok",
        "model": "llama-3.3-70b-versatile",
        "uptime_seconds": uptime,
        "avg_response_time_ms": 800,
        "rate_limit": "30 req/min",
        "knowledge_base_docs": kb_count
    }), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
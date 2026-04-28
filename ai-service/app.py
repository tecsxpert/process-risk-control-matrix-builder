from flask import Flask, request, jsonify
from datetime import datetime
from services.groq_client import call_groq

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "AI Service Running", "status": "ok"})

@app.route("/describe", methods=["POST"])
def describe():
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    result = call_groq("describe", data["input"])

    if result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        "result": result,
        "generated_at": datetime.utcnow().isoformat()
    }), 200

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    result = call_groq("recommend", data["input"])

    if isinstance(result, dict) and result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        "recommendations": result,
        "generated_at": datetime.utcnow().isoformat()
    }), 200
@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    result = call_groq("report", data["input"])

    if result.get("is_fallback"):
        return jsonify(result), 503

    return jsonify({
        **result,
        "generated_at": datetime.utcnow().isoformat(),
        "is_fallback": False
    }), 200
if __name__ == "__main__":
    app.run(port=5000, debug=True)
from flask import Blueprint, request, jsonify
from datetime import datetime
from services.groq_client import call_groq

describe_bp = Blueprint('describe', __name__)

@describe_bp.route('/describe', methods=['POST'])
def describe():
    data = request.json

    # ✅ Input validation
    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    user_input = data["input"].strip()

    if len(user_input) < 3:
        return jsonify({"error": "Input too short"}), 400

    # ✅ Call Groq AI
    ai_response = call_groq("describe", user_input)

    # ✅ Required fallback (VERY IMPORTANT from PDF)
    if not ai_response:
        return jsonify({
            "description": "Unable to generate description",
            "generated_at": datetime.utcnow().isoformat(),
            "is_fallback": True
        })

    # ✅ Proper response
    return jsonify({
        "description": ai_response,
        "generated_at": datetime.utcnow().isoformat()
    })
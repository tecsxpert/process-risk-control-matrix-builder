from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "AI Service Running"}

# ✅ DAY 3 API
@app.route("/describe", methods=["POST"])
def describe():
    data = request.get_json()

    if not data or "input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    user_input = data["input"].lower()

    if "bank" in user_input or "payment" in user_input:
        risks = [
            "Unauthorized transactions",
            "Fraud attacks",
            "Data leakage"
        ]
        controls = [
            "Multi-factor authentication",
            "Transaction monitoring",
            "Data encryption"
        ]

    elif "login" in user_input:
        risks = [
            "Brute force attacks",
            "Password theft",
            "Session hijacking"
        ]
        controls = [
            "Strong passwords",
            "Login attempt limits",
            "Secure sessions"
        ]

    else:
        risks = [
            "System failure",
            "Data loss",
            "Unauthorized access"
        ]
        controls = [
            "Backups",
            "Access control",
            "Monitoring"
        ]

    return jsonify({
        "result": {
            "process_description": f"This process describes {user_input}",
            "risks": risks,
            "controls": controls
        },
        "generated_at": str(datetime.utcnow())
    })


# ✅ DAY 4 API
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    if not data or "risk" not in data:
        return jsonify({"error": "Invalid input"}), 400

    risk = data["risk"].lower()

    if "fraud" in risk:
        recommendations = [
            "Enable transaction alerts",
            "Use fraud detection systems",
            "Monitor unusual activity"
        ]

    elif "unauthorized" in risk:
        recommendations = [
            "Implement strong authentication",
            "Use role-based access",
            "Audit user activity"
        ]

    else:
        recommendations = [
            "Regular monitoring",
            "System updates",
            "Security audits"
        ]

    return jsonify({
        "risk": risk,
        "recommendations": recommendations,
        "generated_at": str(datetime.utcnow())
    })


if __name__ == "__main__":
    app.run(port=5000)
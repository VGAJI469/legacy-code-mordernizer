import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FASTAPI_URL = "http://127.0.0.1:8000"

@app.route("/modernize", methods=["POST"])
def modernize():
    data = request.json
    code = data.get("code", "")
    lower_code = code.lower()

    # 🔹 Detect language to pass to FastAPI
    if "identification division" in lower_code or "procedure division" in lower_code:
        source_language = "cobol"
    elif "public static void main" in lower_code or "system.out.println" in lower_code:
        source_language = "java"
    else:
        source_language = "java"  # Default fallback

    try:
        # Forward request to FastAPI (Teammate 2)
        response = requests.post(f"{FASTAPI_URL}/modernize", json={
            "code": code,
            "source_language": source_language,
            "target_language": "python"  # Defaulting to python for the demo
        }, timeout=60)
        
        response.raise_for_status()
        result = response.json()
        
        # Format the output as React expects
        modernized = result.get("modernized_code", "")
        output = f"# Converted Code (from {result.get('source_language', source_language)})\n\n{modernized}"
        return jsonify({"output": output})
        
    except Exception as e:
        print(f"Error calling FastAPI: {e}")
        return jsonify({"output": f"❌ Error connecting to LLM Backend: {str(e)}"}), 500


@app.route("/metrics/summary", methods=["GET"])
def metrics_summary():
    try:
        response = requests.get(f"{FASTAPI_URL}/metrics/summary", timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/supported-languages", methods=["GET"])
def supported_languages():
    try:
        response = requests.get(f"{FASTAPI_URL}/supported-languages", timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Shows both Flask and FastAPI health status"""
    status = {"flask": "ok", "fastapi": "down"}
    try:
        res = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        if res.status_code == 200:
            status["fastapi"] = res.json()
    except Exception:
        pass
    
    return jsonify(status)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
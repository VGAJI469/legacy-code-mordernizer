from dotenv import load_dotenv
import os

load_dotenv()   
import requests
import json
import os

SCALEDOWN_API_KEY = os.getenv("SCALEDOWN_API_KEY")
SCALEDOWN_URL = "https://api.scaledown.xyz/compress/raw/"

def compress_code(code):
    try:
        headers = {
            "x-api-key": SCALEDOWN_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "context": code,
            "prompt": "Compress this code aggressively by removing redundancy, shortening expressions, and keeping only essential logic. Preserve functionality but minimize size.",
            "scaledown": {
                "rate": "high"
            }
        }

        response = requests.post(
            SCALEDOWN_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=20
        )

        response.raise_for_status()

        result = response.json()

        # Adjust depending on API response
        return result.get("output") or result.get("compressed") or code

    except Exception as e:
        print("ScaleDown failed:", e)
        return code
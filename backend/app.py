from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import json
import os

app = Flask(__name__)
CORS(app)

# Load plant care data
with open("plants.json", "r") as f:
    plant_data = json.load(f)

PLANT_ID_API_KEY = "YOUR_API_KEY_HERE"  # 🔑 Replace with your key
PLANT_ID_URL = "https://api.plant.id/v3/identification"

@app.route("/identify", methods=["POST"])
def identify():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # Convert image to base64
    img_base64 = base64.b64encode(file.read()).decode("utf-8")

    # Prepare request payload
    payload = {
        "images": [img_base64],
        "similar_images": True
    }

    headers = {
        "Content-Type": "application/json",
        "Api-Key": PLANT_ID_API_KEY
    }

    # Call Plant.id API
    response = requests.post(PLANT_ID_URL, headers=headers, json=payload)
    result = response.json()

    try:
        plant_name = result["result"]["classification"]["suggestions"][0]["name"]
    except:
        return jsonify({"error": "Could not identify plant"}), 500

    # Match with care data (fallback if not found)
    care_info = plant_data.get(plant_name, {
        "watering": "General: Water moderately",
        "sunlight": "General: Indirect light preferred",
        "tips": "No specific info available"
    })

    return jsonify({
        "plant": plant_name,
        "care": care_info
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)

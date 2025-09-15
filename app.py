from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Load plant care data
with open("plants.json") as f:
    PLANT_DATA = json.load(f)

PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")

@app.route("/identify", methods=["POST"])
def identify():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image = request.files["image"]

    # Send to Plant.id API
    files = {"images": (image.filename, image, "image/jpeg")}
    response = requests.post(
        "https://api.plant.id/v3/identification",
        headers={"Api-Key": PLANT_ID_API_KEY},
        files=files
    )

    result = response.json()
    suggestions = result.get("result", {}).get("classification", {}).get("suggestions", [])
    if not suggestions:
        return jsonify({"error": "Could not identify plant"}), 400

    plant_name = suggestions[0]["name"]

    care = PLANT_DATA.get(plant_name.lower(), {
        "water": "No data",
        "sunlight": "No data"
    })

    return jsonify({
        "plant": plant_name,
        "care": care
    })

if __name__ == "__main__":
    app.run(debug=True)

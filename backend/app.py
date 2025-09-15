import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PLANTNET_API_URL = "https://my-api.plantnet.org/v2/identify/all"
PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")  # store in .env file

@app.route("/identify", methods=["POST"])
def identify():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    files = {"images": (image.filename, image.stream, image.content_type)}
    headers = {"Api-Key": PLANTNET_API_KEY}
    params = {"organs": ["leaf"]}

    try:
        response = requests.post(PLANTNET_API_URL, files=files, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" in data and data["results"]:
            plant = data["results"][0]["species"]
            return jsonify({
                "plant_name": plant.get("scientificNameWithoutAuthor", "N/A"),
                "common_name": plant.get("commonName", "N/A"),
                "family": plant.get("family", "N/A"),
                "genus": plant.get("genus", "N/A"),
                "image": plant.get("imageUrl", "")
            })
        else:
            return jsonify({"error": "No plant identified"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

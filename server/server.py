from flask import Flask, request, jsonify, render_template
import util
import base64

# Create Flask app and serve static files correctly
app = Flask(
    __name__,
    static_folder="../ui",  # 'ui/' contains CSS, JS, and images
    static_url_path="/static",  # URL will be /static/...
)

# Increase payload size limit (default is only 1MB)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB


# Load your HTML frontend
@app.route("/")
def home():
    return render_template("app.html")


# Image classification endpoint
@app.route("/classify_image", methods=["POST"])
def classify_image():
    # Ensure a file is actually sent
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # Handle case where no file is selected
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        # Read image and convert to base64 (as expected by util.py)
        image_bytes = file.read()
        base64_data = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode()

        # Classify using util.py
        result = util.classify_image(image_base64_data=base64_data)
        print("Prediction result:", result)

        return jsonify(result)

    except Exception as e:
        print("Error during classification:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting Python Flask Server For Sports Celebrity Image Classification")
    util.load_saved_artifacts()
    app.run(port=5000, debug=True)

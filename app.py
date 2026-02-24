from dotenv import load_dotenv
from flask import Flask, request, jsonify
from func import getPdfData, getCumplimientoData
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3001"}})
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    print("Received upload request", request.files)
    if "file" not in request.files:
        return jsonify({"error": "No file received"}), 400

    try:
        file_list = request.files.getlist("file")  # Get all files
        for file in file_list:
            getPdfData(file)  # Pass the file object directly to getPdfData
            return (
                jsonify(
                    {
                        "message": "Files processed successfully",
                        "filenames": [file.filename for file in file_list],
                    }
                ),
                200,
            )

    except Exception as e:
        print("Error processing files:", e)
        return jsonify({"error": "Error processing files"}), 500


@app.route("/cumplimiento", methods=["GET", "POST"])
def cumplimiento():
    data = getCumplimientoData()
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask import request
from func import getPdfData, getCumplimientoData
import os
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGIN")}})  # Enable CORS for the specified origin
CORS(app)  # Enable CORS for all origins (for testing purposes, adjust in production)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Tax Compliance Microservice API", 200

@app.route("/upload", methods=["POST"])
def upload():
    logging.info("Received request to /upload endpoint")
    logging.info("Request content type: %s", request.content_type)
    logging.info("Request headers: %s", request.headers)
    logging.info("Request DATA: %s", request.data)
    logging.info("Request method: %s", request.method)
    logging.info("Request files: %s", request.files)
    logging.info("Request from backenddata endpoint upload: %s", request.form)

    try:
        # Get all files sent under the "file" field
        file_list = request.form.to_dict(flat=False).get("files", [])

        if not file_list:
            return jsonify({"error": "No files received"}), 400

        processed_files = []

        for file in file_list:
            logging.info("Processing file: %s", file.filename)
            logging.info("MIME type: %s", file.mimetype)
            logging.info("Size (bytes): %d", len(file.read()))
            file.seek(0)  # Reset file pointer after reading
            getPdfData(file)
            processed_files.append(file.filename)

        return jsonify({
            "message": "Files processed successfully",
            "filenames": processed_files
        }), 200

    except Exception as e:
        logging.error("Error processing files: %s", e)
        return jsonify({"error": "Error processing files", "details": str(e)}), 500


@app.route("/cumplimiento", methods=["GET", "POST"])
def cumplimiento():
    logging.info("Received request to /cumplimiento endpoint")
    logging.info("Request method: %s", request.method)
    
    data = getCumplimientoData()
    return jsonify(data), 200


#if __name__ == "__main__":
 #   app.run(host="localhost", port=5000, debug=True)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from db import Connector
import logic
import os
import zipfile
import shutil
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024  # 2048 MB

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


@app.route('/api/fs/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files selected"}), 400

    result = logic.save_files(files, app.config['UPLOAD_FOLDER'])

    if result["error"]:
        return jsonify({"error": result["error"]}), 500

    download_link = f"https://bryhas.com/getfs/{result['identifier']}"
    return jsonify({"link": download_link})


@app.route('/api/fs/info/<identifier>', methods=['GET'])
def get_file_info(identifier):
    if logic.validate_identifier(identifier):
        file_info = logic.get_file_info(identifier)
        if file_info:
            return jsonify(file_info)
    return jsonify({"error": "Invalid or non-existent file identifier."}), 404


@app.route('/api/fs/download/<identifier>', methods=['GET'])
def download_files(identifier):
    try:
        if logic.validate_identifier(identifier):
            folder_path = logic.get_folder_path(identifier, app.config['UPLOAD_FOLDER'])
            if folder_path:
                files = os.listdir(folder_path)
                if len(files) == 1:
                    # 1 file send
                    return send_from_directory(folder_path, files[0], as_attachment=True)
                else:
                    # zip for multiple files
                    zip_path = os.path.join(folder_path, f"{identifier}.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for file in files:
                            zipf.write(os.path.join(folder_path, file), file)
                    return send_from_directory(folder_path, f"{identifier}.zip", as_attachment=True)
            return jsonify({"error": "Folder not found"}), 404
        return jsonify({"error": "Invalid identifier format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fs/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = Connector.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_expired_files():
    logger.debug("Scheduled task started for deleting expired files.")
    now = datetime.now()
    logger.debug(f"Checking for expired files at {now}")
    expired_files = Connector.get_expired_files(now)
    logger.debug(f"Found {len(expired_files)} expired files.")

    for identifier in expired_files:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], identifier)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                logger.debug(f"Successfully deleted folder for identifier: {identifier}")
                Connector.delete_upload_record(identifier)
                logger.debug(f"Successfully deleted database record for identifier: {identifier}")
            except Exception as e:
                logger.error(f"Error deleting folder {folder_path}: {e}")
        else:
            logger.debug(f"Folder not found for identifier: {identifier}")


if __name__ == '__main__':
    logger.debug("Starting the Flask application...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=delete_expired_files, trigger="interval", seconds=30)
    scheduler.start()
    logger.debug("Scheduler started.")
    app.run(host='0.0.0.0', port=4999)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logic

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024  # 2048 MB


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
    return jsonify({"error": "Invalid or non-existent file identifier."}), 400


@app.route('/api/fs/download/<identifier>', methods=['GET'])
def download_files(identifier):
    if logic.validate_identifier(identifier):
        folder_path = logic.get_folder_path(identifier, app.config['UPLOAD_FOLDER'])
        if folder_path:
            return send_from_directory(directory=folder_path, filename='', as_attachment=True)
    return jsonify({"error": "Invalid or non-existent file identifier."}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4999)

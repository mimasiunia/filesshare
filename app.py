from flask import Flask, request, jsonify
from flask_cors import CORS
import logic

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'data'


@app.route('/upload', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4999)

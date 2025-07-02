import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid

from app import App

flask_app = Flask(__name__)
flask_app.config['UPLOAD_FOLDER'] = 'uploads'
flask_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/search")
def search():
    search_query = request.args.get("search_query")
    app = App()
    results = app.search_by_text(search_query, results=5)
    return jsonify(results)

@flask_app.route("/search_by_image", methods=['POST'])
def search_by_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Save uploaded file with unique name
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            app = App()
            results = app.search_by_image(filepath, results=5)
            # Clean up uploaded file
            os.remove(filepath)
            return jsonify(results)
        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@flask_app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

if __name__ == "__main__":
    flask_app.run(port=5000, debug=True)
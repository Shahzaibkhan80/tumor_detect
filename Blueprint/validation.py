import os
from flask import Blueprint, current_app, jsonify, request
from function.helpers import allowed_file
from function.valid import is_valid_biopsy, is_valid_xray
from werkzeug.utils import secure_filename

validate_bp = Blueprint('validate', __name__, template_folder='../templates')

@validate_bp.route('/validate', methods=['POST'])
def validate_image():
    try:
        file = request.files.get('file') 
        category = request.form.get('category')  
        if file and category:
            if not allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            if os.path.exists(filepath):
                return jsonify({"error": "File already exists"}), 400

            file.save(filepath)

            if category == 'xray':
                is_valid = is_valid_xray(filepath)
                return jsonify({"message": "Valid X-ray image" if is_valid else "Invalid X-ray image"})
            elif category == 'biopsy':
                is_valid = is_valid_biopsy(filepath)
                return jsonify({"message": "Valid biopsy image" if is_valid else "Invalid biopsy image"})
            else:
                return jsonify({"error": "Unknown category"}), 400

        return jsonify({"error": "No file uploaded or category missing"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

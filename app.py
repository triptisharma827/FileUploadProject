from flask import Flask, request, jsonify
import os
import boto3
from docx2pdf import convert
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

BUCKET_NAME = 'your-s3-bucket-name'  # Replace with your S3 bucket name

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_pdf(file_path):
    try:
        pdf_path = file_path.rsplit('.', 1)[0] + '.pdf'
        convert(file_path, pdf_path)
        return pdf_path
    except Exception as e:
        print(e)
        return None

def upload_to_s3(file_path, filename):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, BUCKET_NAME, filename)

@app.route('/convert', methods=['POST'])
def convert_word_to_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename) and file.content_length <= MAX_FILE_SIZE:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        pdf_path = convert_to_pdf(file_path)
        if pdf_path:
            upload_to_s3(pdf_path, filename)
            return jsonify({'message': 'File converted and uploaded successfully'})
        else:
            return jsonify({'error': 'Failed to convert file to PDF'}), 500
    else:
        return jsonify({'error': 'Invalid file format or size exceeded'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=1010)

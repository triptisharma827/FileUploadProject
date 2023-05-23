import os
import boto3
from docx2pdf import convert

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    if 'body' not in event:
        return {'statusCode': 400, 'body': 'No request body'}

    request_body = event['body']
    file_obj = get_file_from_formdata(request_body)

    if not file_obj:
        return {'statusCode': 400, 'body': 'No file in the request'}

    file_name = file_obj['filename']
    file_content = file_obj['content']
    file_size = len(file_content)

    if file_size > 5 * 1024 * 1024:
        return {'statusCode': 400, 'body': 'File size exceeded (5 MB limit)'}

    file_path = f'/tmp/{file_name}'
    with open(file_path, 'wb') as f:
        f.write(file_content)

    pdf_path = convert_to_pdf(file_path)
    if pdf_path:
        upload_to_s3(pdf_path, file_name)
        return {'statusCode': 200, 'body': 'File converted and uploaded successfully'}
    else:
        return {'statusCode': 500, 'body': 'Failed to convert file to PDF'}

def get_file_from_formdata(request_body):
    for part in request_body:
        if part.filename:
            return {
                'filename': part.filename,
                'content': part.read()
            }
    return None

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
import boto3
import os
from docx2pdf import convert

def lambda_handler(event, context):
    # Check if the headers attribute is present in the event
    if 'headers' not in event:
        return {
            'statusCode': 400,
            'body': {
                'error': 'Invalid request. Headers not found in the request.'
            }
        }

    # Get the content type from the headers
    headers = event['headers']
    if 'Content-Type' not in headers:
        return {
            'statusCode': 400,
            'body': {
                'error': 'Invalid request. Content-Type header not found.'
            }
        }
    content_type = headers['Content-Type']

    # Check if the content type is multipart/form-data
    if 'multipart/form-data' not in content_type:
        return {
            'statusCode': 400,
            'body': {
                'error': 'Invalid request. Content-Type must be multipart/form-data.'
            }
        }

    # Get the file from the event
    file_data = None
    if 'body' in event:
        body = event['body']
        for part in body:
            if 'content-type' in part and 'filename' in part:
                if part['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    file_data = part['content']
                    break

    if file_data is None:
        return {
            'statusCode': 400,
            'body': {
                'error': 'Invalid request. File not found in the request body.'
            }
        }

    # Convert the file_data to bytes
    file_bytes = file_data.encode('utf-8')

    # Create a temporary file to store the uploaded file
    with open('/tmp/uploaded_file.docx', 'wb') as f:
        f.write(file_bytes)

    # Check if the file is a .docx file
    if not file_data.lower().endswith('.docx'):
        return {
            'statusCode': 400,
            'body': {
                'error': 'Invalid file format. File is not a .docx file.'
            }
        }

    # Convert the .docx file to .pdf
    pdf_bytes = convert('/tmp/uploaded_file.docx')

    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename('/tmp/uploaded_file.docx'))[0]

    # Specify the key/path for the output PDF file
    pdf_key = f'{file_name}.pdf'

    # Save the PDF file to an S3 bucket
    s3 = boto3.resource('s3')
    bucket_name = 'pdf-files-storage'  # Replace with your S3 bucket name
    s3.Bucket(bucket_name).put_object(Key=pdf_key, Body=pdf_bytes)

    return {
        'statusCode': 200,
        'body': {
            'message': 'Word document converted and PDF stored successfully!'
        }
    }

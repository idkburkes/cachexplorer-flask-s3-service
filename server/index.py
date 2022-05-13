"""
Handles signing uploads correctly
"""
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
import boto3
import mimetypes
import os
from dotenv import load_dotenv

# Setup
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['CORS_HEADERS'] = 'Content-Type'
load_dotenv()

# Environment Variables
AWS_KEY = os.getenv('AWS_KEY')
AWS_SECRET = os.getenv('AWS_SECRET')
AWS_BUCKET = os.getenv('AWS_BUCKET')

session = boto3.Session(aws_access_key_id=AWS_KEY,
                        aws_secret_access_key=AWS_SECRET)
s3 = session.client('s3', region_name='us-east-1')


@app.route('/')
def home():
  return f"<p> Cachexplorer Flask S3 Service is running</p>"

@app.route('/upload/sign')
def sign_upload():
  object_name = request.args['objectName']
  content_type = mimetypes.guess_type(object_name)[0]

  # create signed url for PUT request
  signed_url = s3.generate_presigned_url(
      'put_object', {'Bucket': AWS_BUCKET,
                     'Key': object_name, 'ContentType': content_type, 'ACL': 'public-read'}, ExpiresIn=3600, HttpMethod='PUT')

  # reference URL for uploaded object
  url = 'https://cache-explorer.s3.amazonaws.com/' + object_name

  print(url)
  response = jsonify({'signedUrl': signed_url, 'url': url, 'key': object_name})

  response.headers.add("Access-Control-Allow-Credentials", "true")
  return response

@app.route('/upload/image')
# uploads a file to s3 from flask server
# returns the url to the uploaded file
def upload_file(file_path):
  # get the file name from the file path
  key = file_path.rsplit('/', 1)[-1]
  content_type = mimetypes.guess_type(key)[0]

  s3 = session.resource('s3')
  s3.meta.client.upload_file(
      Filename=file_path, Bucket=AWS_BUCKET, Key=key, ExtraArgs={'ContentType': content_type, 'ACL': "public-read"})

  url = 'https://cache-explorer.s3.amazonaws.com//' + key
  return url



if __name__ == '__main__':
  app.run(use_reloader=True, port=5000, threaded=True)
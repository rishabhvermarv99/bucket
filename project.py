from flask import Flask, render_template, request, redirect, flash
import boto3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# AWS S3 configurations (use environment variables or a config file)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Error handling function
def handle_error_and_redirect(e, message):
    flash(f"Error: {str(e)} - {message}")
    return redirect('/')

@app.route('/')
def index():
    try:
        # List buckets
        buckets = s3.list_buckets()['Buckets']
        return render_template('index.html', buckets=buckets)
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to list buckets")

@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    try:
        bucket_name = request.form['bucket_name']
        s3.create_bucket(Bucket=bucket_name)
        flash(f"Bucket '{bucket_name}' created successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to create bucket")
    

@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    try:
        bucket_name = request.form['bucket_name']
        s3.delete_bucket(Bucket=bucket_name)
        flash(f"Bucket '{bucket_name}' deleted successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to delete bucket")

@app.route('/create_folder', methods=['POST'])
def create_folder():
    try:
        bucket_name = request.form['bucket_name']
        folder_name = request.form['folder_name']
        s3.put_object(Bucket=bucket_name, Key=folder_name + '/')
        flash(f"Folder '{folder_name}' created in '{bucket_name}' successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to create folder")

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    try:
        bucket_name = request.form['bucket_name']
        folder_name = request.form['folder_name']

        # List objects in the folder
        response = s3.list_objects(Bucket=bucket_name, Prefix=folder_name + '/')
        objects = response.get('Contents', [])

        # Delete individual objects in the folder
        for obj in objects:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])

        # Delete the folder itself
        s3.delete_object(Bucket=bucket_name, Key=folder_name + '/')
        flash(f"Folder '{folder_name}' deleted from '{bucket_name}' successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to delete folder")

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        bucket_name = request.form['bucket_name']
        folder_name = request.form['folder_name']
        file = request.files['file']

        # Upload the file to the folder
        s3.upload_fileobj(file, bucket_name, folder_name + '/' + file.filename)
        flash(f"File '{file.filename}' uploaded to '{bucket_name}/{folder_name}' successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to upload file")

@app.route('/copy_file', methods=['POST'])
def copy_file():
    try:
        src_bucket = request.form['src_bucket']
        src_file_key = request.form['src_file_key']
        dest_bucket = request.form['dest_bucket']
        dest_file_key = request.form['dest_file_key']

        # Copy the file to the destination
        s3.copy_object(Bucket=dest_bucket,
                       CopySource={'Bucket': src_bucket, 'Key': src_file_key},
                       Key=dest_file_key)

        flash(f"File '{src_file_key}' copied to '{dest_bucket}' as '{dest_file_key}' successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to copy file")

@app.route('/move_file', methods=['POST'])
def move_file():
    try:
        src_bucket = request.form['src_bucket']
        src_file_key = request.form['src_file_key']
        dest_bucket = request.form['dest_bucket']
        dest_file_key = request.form['dest_file_key']

        # Copy the file to the destination
        s3.copy_object(Bucket=dest_bucket,
                       CopySource={'Bucket': src_bucket, 'Key': src_file_key},
                       Key=dest_file_key)

        # Delete the original file
        s3.delete_object(Bucket=src_bucket, Key=src_file_key)

        flash(f"File '{src_file_key}' moved to '{dest_bucket}' as '{dest_file_key}' successfully!")
        return redirect('/')
    except Exception as e:
        return handle_error_and_redirect(e, "Failed to move file")

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
import boto3

# # Provide AWS credentials directly
# access_key = 'AKIASAAA7EGUACLZKMMF'
# secret_key = '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'

# # Create an S3 client with the provided credentials
# s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# Perform operations with the S3 client
# ...



app = Flask(__name__)
s3 = boto3.client("s3")

@app.route("/")
def index():
    buckets = s3.list_buckets()
    return render_template("index.html", buckets=buckets["Buckets"])

@app.route("/bucket/<bucket_name>")
def show_bucket(bucket_name):
    objects = s3.list_objects_v2(Bucket=bucket_name)
    if "Contents" in objects:
        contents = objects["Contents"]
    else:
        contents = []
    return render_template("bucket.html", bucket_name=bucket_name, contents=contents)

@app.route("/create_bucket", methods=["POST"])
def create_bucket():
    bucket_name = request.form["bucket_name"]
    s3.create_bucket(Bucket=bucket_name)
    return redirect("/")

@app.route("/delete_bucket/<bucket_name>")
def delete_bucket(bucket_name):
    s3.delete_bucket(Bucket=bucket_name)
    return redirect("/")

@app.route("/upload_file", methods=["POST"])
def upload_file():
    bucket_name = request.form["bucket_name"]
    file = request.files["file"]
    s3.upload_fileobj(file, bucket_name, file.filename)
    return redirect(f"/bucket/{bucket_name}")

@app.route("/delete_file/<bucket_name>/<key>")
def delete_file(bucket_name, key):
    s3.delete_object(Bucket=bucket_name, Key=key)
    return redirect(f"/bucket/{bucket_name}")

@app.route("/copy_file", methods=["POST"])
def copy_file():
    source_bucket = request.form["source_bucket"]
    destination_bucket = request.form["destination_bucket"]
    key = request.form["key"]
    s3.copy_object(
        Bucket=destination_bucket,
        CopySource={"Bucket": source_bucket, "Key": key},
        Key=key
    )
    return redirect(f"/bucket/{destination_bucket}")

@app.route("/move_file", methods=["POST"])
def move_file():
    source_bucket = request.form["source_bucket"]
    destination_bucket = request.form["destination_bucket"]
    key = request.form["key"]
    s3.copy_object(
        Bucket=destination_bucket,
        CopySource={"Bucket": source_bucket, "Key": key},
        Key=key
    )
    s3.delete_object(Bucket=source_bucket, Key=key)
    return redirect(f"/bucket/{destination_bucket}")

if __name__ == "__main__":
    app.run(debug=True)

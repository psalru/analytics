import os
import boto3
from io import StringIO, BytesIO
from dotenv import load_dotenv

load_dotenv()
S3_HOST = os.getenv("S3_HOST")
S3_REGION_NAME = os.getenv("S3_REGION_NAME")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_ACCESS_KEY_SECRET = os.getenv('S3_ACCESS_KEY_SECRET')


def get_str(key: str, bucket=S3_BUCKET) -> str:
    obj = s3.get_object(Bucket=bucket, Key=key)

    return obj['Body'].read().decode('utf-8')


def get_csv(key: str, bucket=S3_BUCKET):
    string = get_str(key, bucket)

    return StringIO(string)


def get_excel(key: str, bucket=S3_BUCKET):
    obj = s3.get_object(Bucket=bucket, Key=key)

    return BytesIO(obj['Body'].read())


conn = boto3.session.Session(aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_ACCESS_KEY_SECRET, region_name=S3_REGION_NAME)
s3 = conn.client(service_name='s3', endpoint_url=S3_HOST)

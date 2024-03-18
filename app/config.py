import os

from dotenv import load_dotenv

load_dotenv()

S3_KEY_ID = os.environ.get("S3_KEY_ID")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET")


REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")



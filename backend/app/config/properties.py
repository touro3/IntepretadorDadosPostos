import os
from dotenv import load_dotenv

load_dotenv(override=True)

AZURE_LLM_API_KEY = os.getenv("AZURE_LLM_API_KEY")
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
POSTGRES_URI = os.getenv("POSTGRES_URI")

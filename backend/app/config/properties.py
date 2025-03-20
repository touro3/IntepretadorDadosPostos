import os
from dotenv import load_dotenv

load_dotenv()

AZURE_LLM_API_KEY = os.getenv("AZURE_LLM_API_KEY")
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY")

# from config.properties import AZURE_OPENAI_API_KEY
import os
from llama_index.llms.ollama import Ollama

# Use host.docker.internal to connect to host machine from Docker container
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

llm = Ollama(model="codellama:7b", request_timeout=60.0, base_url=ollama_base_url)
# from openai import AzureOpenAI

# client = AzureOpenAI(
#     api_key=AZURE_OPENAI_API_KEY,
#     api_version="2024-12-01-preview",
#     azure_endpoint="https://marco-mamvt9zp-eastus2.cognitiveservices.azure.com/",
# )

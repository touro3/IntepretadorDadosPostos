from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

llm = Ollama(model="gemma3:12b")
embedding = HuggingFaceEmbedding(model_name="paraphrase-multilingual-MiniLM-L12-v2")

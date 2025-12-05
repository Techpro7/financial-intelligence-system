# financial_news_intel/core/config.py

import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
# This must be the first thing done in a configuration file.
load_dotenv() 

# --- LLM Configuration (Ollama) ---
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- Embedding Model Configuration ---
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# --- NER Model Configuration  ---
SPACY_MODEL_NAME = os.getenv("SPACY_MODEL_NAME", "en_core_web_md")

# --- Vector Database (ChromaDB) ---
# CRITICAL NEW VARIABLES
CHROMA_DB_MODE = os.getenv("CHROMA_DB_MODE", "local")  # New: 'local' (file) or 'remote' (server)
CHROMA_DB_URL = os.getenv("CHROMA_DB_URL", "http://localhost:8000") # New: Server address

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data") # Existing
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "financial_news_dedup") # Existing
CHROMA_RAG_COLLECTION_NAME = os.getenv("CHROMA_RAG_COLLECTION_NAME", "financial_news_rag") # New for RAG

# --- RAG and Deduplication Configuration ---
try:
    # Convert the string from .env to a float
    DEDUPLICATION_SIMILARITY_THRESHOLD = float(os.getenv("DEDUPLICATION_SIMILARITY_THRESHOLD", 0.95))
except ValueError:
    DEDUPLICATION_SIMILARITY_THRESHOLD = 0.95
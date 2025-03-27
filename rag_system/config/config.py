import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
DOCUMENTS_DIR = DATA_DIR / "documents"

# Créer les répertoires s'ils n'existent pas
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# Configuration ElasticSearch
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "rag_documents")

# Configuration du modèle LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # 'gemini' ou 'ollama'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Configuration des embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Configuration de l'application
APP_NAME = "Système RAG avec ElasticSearch et LangChain"
APP_DESCRIPTION = "Système de Retrieval Augmented Generation pour répondre aux questions basées sur vos documents" 
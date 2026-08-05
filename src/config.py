"""
==========================================================
Incident Knowledge Assistant (RAG)

config.py

Author : Pramod Prakash Jadhav
==========================================================

Central configuration file for the complete RAG application.
"""

from pathlib import Path

# ==========================================================
# Project Information
# ==========================================================

PROJECT_NAME = "Incident Knowledge Assistant"

PROJECT_VERSION = "1.0.0"

AUTHOR = "Pramod Prakash Jadhav"

DESCRIPTION = (
    "Retrieval-Augmented Generation (RAG) "
    "application for Incident Knowledge Search."
)

# ==========================================================
# Root Directories
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

SRC_DIR = ROOT_DIR / "src"

PAGES_DIR = ROOT_DIR / "pages"

OUTPUT_DIR = ROOT_DIR / "outputs"

LOG_DIR = OUTPUT_DIR / "logs"

VECTOR_STORE_DIR = ROOT_DIR / "vector_store"

# ==========================================================
# Data Files
# ==========================================================

DATASET_PATH = (
    DATA_DIR / "incidents.csv"
)

FAISS_INDEX_PATH = (
    VECTOR_STORE_DIR / "faiss.index"
)

DOCUMENTS_PATH = (
    VECTOR_STORE_DIR / "documents.pkl"
)

# ==========================================================
# Output Files
# ==========================================================

LOG_FILE = (
    LOG_DIR / "application.log"
)

EMBEDDINGS_FILE = (
    OUTPUT_DIR / "embeddings.npy"
)

SEARCH_RESULTS_FILE = (
    OUTPUT_DIR / "search_results.csv"
)

CHAT_HISTORY_FILE = (
    OUTPUT_DIR / "chat_history.json"
)

# ==========================================================
# Directory Creation
# ==========================================================

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

VECTOR_STORE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
# ==========================================================
# Embedding Configuration
# ==========================================================

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

EMBEDDING_BATCH_SIZE = 32

NORMALIZE_EMBEDDINGS = True

# ==========================================================
# Vector Store Configuration
# ==========================================================

VECTOR_INDEX_TYPE = "IndexFlatL2"

VECTOR_DISTANCE_METRIC = "L2"

# ==========================================================
# Retrieval Configuration
# ==========================================================

TOP_K_RESULTS = 5

MINIMUM_SIMILARITY_SCORE = 0.0

MAX_CONTEXT_DOCUMENTS = 5

# ==========================================================
# ==========================================================
# Groq Configuration
# ==========================================================

GROQ_MODEL = "llama-3.1-8b-instant"

REQUEST_TIMEOUT = 120

# ==========================================================
# LLM Generation Parameters
# ==========================================================

TEMPERATURE = 0.2

TOP_P = 0.90

TOP_K = 40

MAX_TOKENS = 1024

REPEAT_PENALTY = 1.10

# ==========================================================
# Prompt Configuration
# ==========================================================

SYSTEM_PROMPT = """
You are an AI Incident Knowledge Assistant.

Answer ONLY using the supplied context.

If the answer is not available in the retrieved
documents, clearly respond that the information
is not available in the knowledge base.

Do not hallucinate.

Always provide clear, concise and professional
responses.
"""

USER_PROMPT_TEMPLATE = """
Context:
{context}

Question:
{question}

Answer:
"""
# ==========================================================
# Streamlit Configuration
# ==========================================================

PAGE_TITLE = "Incident Knowledge Assistant"

PAGE_ICON = "🤖"

LAYOUT = "wide"

INITIAL_SIDEBAR_STATE = "expanded"

# ==========================================================
# Analytics Configuration
# ==========================================================

MAX_ANALYTICS_RECORDS = 100

DEFAULT_CHART_HEIGHT = 450

SHOW_RETRIEVAL_SCORES = True

SHOW_DOCUMENT_PREVIEW = True

# ==========================================================
# Logging Configuration
# ==========================================================

LOG_LEVEL = "INFO"

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

# ==========================================================
# Application Constants
# ==========================================================

SUPPORTED_FILE_TYPES = [
    ".csv",
    ".txt",
]

DEFAULT_ENCODING = "utf-8"

APPLICATION_NAME = PROJECT_NAME

APPLICATION_VERSION = PROJECT_VERSION

# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print(PROJECT_NAME)
    print("=" * 60)

    print(f"Version              : {PROJECT_VERSION}")
    print(f"Author               : {AUTHOR}")

    print("\nDirectories")
    print(f"ROOT_DIR             : {ROOT_DIR}")
    print(f"DATA_DIR             : {DATA_DIR}")
    print(f"OUTPUT_DIR           : {OUTPUT_DIR}")
    print(f"VECTOR_STORE_DIR     : {VECTOR_STORE_DIR}")

    print("\nFiles")
    print(f"Dataset              : {DATASET_PATH}")
    print(f"FAISS Index          : {FAISS_INDEX_PATH}")
    print(f"Documents            : {DOCUMENTS_PATH}")
    print(f"Log File             : {LOG_FILE}")

    print("\nEmbedding")
    print(f"Model                : {EMBEDDING_MODEL}")

    print("\nRetriever")
    print(f"Top-K Results        : {TOP_K_RESULTS}")

    print("\nLLM")
    print(f"Ollama URL           : {OLLAMA_BASE_URL}")
    print(f"Model                : {OLLAMA_MODEL}")

    print("\nConfiguration loaded successfully.")
    print("=" * 60)

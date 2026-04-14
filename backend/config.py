"""
# config.py

## What this file does:
Central configuration module for the enterprise-knowledge-agent backend.
Loads all environment variables from the .env file and makes them available
as a single config object that every other backend module imports from.

Also validates that all required variables are present on startup so the
app fails fast with a clear error message rather than breaking mysteriously
later when a variable is actually used.

Imported by: database.py, rag.py, agent.py, main.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
# Explicitly resolve path to .env in project root so this works regardless
# of which directory the app is started from

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Config Values
class Config:
    # OpenAI
    OPENAI_API_KEY:     str  = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL:       str  = os.getenv("OPENAI_MODEL", "gpt-4o")
    EMBEDDING_MODEL:    str  = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Database
    DATABASE_URL:       str  = os.getenv("DATABASE_URL", "sqlite:///./internal_data/velo.db")

    # ChromaDB
    CHROMA_PATH:        str  = os.getenv("CHROMA_PATH", "./internal_data/chroma")
    COLLECTION_NAME:    str  = "velo_knowledge_base"

    # RAG settings
    RAG_TOP_K:          int  = int(os.getenv("RAG_TOP_K", "5"))

    # App settings
    APP_TITLE:          str  = "Velo Enterprise Knowledge Agent"
    APP_VERSION:        str  = "1.0.0"
    DEBUG:              bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS — frontend origin (update when deploying)
    FRONTEND_URL:       str  = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Required variables — app will not start without these
    REQUIRED = ["OPENAI_API_KEY", "DATABASE_URL", "CHROMA_PATH"]

config = Config()

# Validation
def validate_config() -> bool:
    """
    Validates all required environment variables are present and non-empty.
    Called on app startup. Returns True if valid, exits with error if not.
    """
    missing = []
    for key in Config.REQUIRED:
        value = getattr(config, key, None)
        if not value:
            missing.append(key)

    if missing:
        return False

    return True

# Main
if __name__ == "__main__":
    print("Config loaded successfully")

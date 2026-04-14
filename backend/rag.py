"""
# rag.py

## What this file does:
Manages the connection to ChromaDB and provides retrieval functions
that the LangChain agent uses as its RAG tool. When the agent needs
to search company documents it calls the functions in this file.

Key functions:
- get_collection(): returns the ChromaDB collection
- retrieve_docs(): takes a query string and returns the most relevant
  document chunks with their source metadata
- retrieve_docs_for_role(): same as above but filtered by employee role
  so engineering questions prioritize engineering docs

Imported by: agent.py
"""

import sys
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from config import config

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ChromaDB Client
embedding_fn = OpenAIEmbeddingFunction(
    api_key=config.OPENAI_API_KEY,
    model_name=config.EMBEDDING_MODEL,
)

chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)


def get_collection():
    """Returns the Velo knowledge base ChromaDB collection."""
    return chroma_client.get_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_fn,
    )


# Retrieval Functions
def retrieve_docs(query: str, n_results: int = None) -> str:
    """
    Retrieves the most semantically relevant document chunks for a query.
    Returns a formatted string the LangChain agent can read directly.

    Args:
        query:     Natural language question or search string
        n_results: Number of chunks to retrieve (defaults to RAG_TOP_K in config)

    Returns:
        Formatted string of relevant document excerpts with source labels
    """
    if n_results is None:
        n_results = config.RAG_TOP_K

    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    if not results or not results["documents"][0]:
        return "No relevant documents found for this query."

    formatted = []
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        source   = meta.get("source", "Unknown")
        doc_name = meta.get("doc_name", source)
        formatted.append(
            f"[Source: {doc_name}]\n{doc}"
        )

    return "\n\n---\n\n".join(formatted)


def retrieve_docs_for_role(query: str, role: str, n_results: int = None) -> str:
    """
    Retrieves relevant document chunks filtered by employee role.
    First tries role-specific docs, falls back to all docs if needed.

    Args:
        query:     Natural language question
        role:      Employee role — 'engineering', 'sales', 'customer_success', 'all'
        n_results: Number of chunks to retrieve

    Returns:
        Formatted string of relevant document excerpts with source labels
    """
    if n_results is None:
        n_results = config.RAG_TOP_K

    collection = get_collection()

    # Try role-specific retrieval first
    if role and role != "all":
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"relevant_to": {"$in": [role, "all"]}},
            )
            if results and results["documents"][0]:
                formatted = []
                for i, (doc, meta) in enumerate(
                    zip(results["documents"][0], results["metadatas"][0])
                ):
                    source   = meta.get("source", "Unknown")
                    doc_name = meta.get("doc_name", source)
                    formatted.append(f"[Source: {doc_name}]\n{doc}")
                return "\n\n---\n\n".join(formatted)
        except Exception:
            pass

    # Fall back to unfiltered retrieval
    return retrieve_docs(query, n_results)

def get_role_from_persona(persona: str) -> str:
    """Maps a persona type to a ChromaDB role filter value."""
    mapping = {
        "new_hire": "all",
        "manager":  "sales",
        "ops":      "all",
        "exec":     "customer_success",
    }
    return mapping.get(persona, "all")

# Main
if __name__ == "__main__":
    print("RAG pipeline verified")

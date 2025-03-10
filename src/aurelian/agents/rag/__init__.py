"""
RAG agent package for retrieval-augmented generation against document collections.
"""

# Constants
COLLECTION_NAME = "main"

# isort: skip_file
from .rag_agent import rag_agent  # noqa: E402
from .rag_config import RagDependencies, get_config  # noqa: E402
from .rag_gradio import chat  # noqa: E402
from .rag_tools import (  # noqa: E402
    search_documents,
    inspect_document,
    lookup_pmid,
    search_web,
    retrieve_web_page,
)

__all__ = [
    # Constants
    "COLLECTION_NAME",
    
    # Agent
    "rag_agent",
    
    # Config
    "RagDependencies",
    "get_config",
    
    # Tools
    "search_documents",
    "inspect_document",
    "lookup_pmid",
    "search_web",
    "retrieve_web_page",
    
    # Gradio
    "chat",
]
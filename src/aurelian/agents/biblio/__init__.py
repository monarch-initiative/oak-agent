"""
Biblio agent package for working with bibliographic data and citations.
"""

# Constants
HANDLE = "mongodb://localhost:27017/biblio"
DB_NAME = "biblio"
COLLECTION_NAME = "main"

# isort: skip_file
from .biblio_agent import biblio_agent  # noqa: E402
from .biblio_config import BiblioDependencies, get_config  # noqa: E402
from .biblio_gradio import chat  # noqa: E402
from .biblio_tools import (  # noqa: E402
    search_bibliography,
    lookup_pmid,
    search_web,
    retrieve_web_page,
)

__all__ = [
    # Constants
    "HANDLE",
    "DB_NAME",
    "COLLECTION_NAME",
    
    # Agent
    "biblio_agent",
    
    # Config
    "BiblioDependencies",
    "get_config",
    
    # Tools
    "search_bibliography",
    "lookup_pmid",
    "search_web",
    "retrieve_web_page",
    
    # Gradio
    "chat",
]
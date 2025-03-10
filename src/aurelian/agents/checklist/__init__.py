"""
Checklist agent package for validating papers against checklists (e.g., STREAMS).
"""
from pathlib import Path

THIS_DIR = Path(__file__).parent
CONTENT_DIR = THIS_DIR / "content"
CONTENT_METADATA_PATH = CONTENT_DIR / "checklists.yaml"

# These imports must be after constants are defined
# isort: skip_file
from .checklist_agent import checklist_agent, add_checklists  # noqa: E402
from .checklist_config import ChecklistDependencies, get_config  # noqa: E402
from .checklist_gradio import chat  # noqa: E402
from .checklist_tools import (  # noqa: E402
    all_checklists,
    retrieve_text_from_pmid,
    retrieve_text_from_doi,
    fetch_checklist,
)

__all__ = [
    # Constants
    "THIS_DIR",
    "CONTENT_DIR",
    "CONTENT_METADATA_PATH",
    
    # Agent
    "checklist_agent",
    "add_checklists",
    
    # Config
    "ChecklistDependencies",
    "get_config",
    
    # Tools
    "all_checklists",
    "retrieve_text_from_pmid",
    "retrieve_text_from_doi",
    "fetch_checklist",
    
    # Gradio
    "chat",
]

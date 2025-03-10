"""
DEPRECATED: This module has been refactored into the gocam/ subdirectory.

This file remains for backward compatibility, but you should use:
- aurelian.agents.gocam.gocam_agent
- aurelian.agents.gocam.gocam_config
- aurelian.agents.gocam.gocam_tools
- aurelian.agents.gocam.gocam_gradio
"""

# Re-export from new location
from aurelian.agents.gocam.gocam_agent import gocam_agent
from aurelian.agents.gocam.gocam_config import GOCAMDependencies as GOCamDependencies  # Alias for backward compatibility
from aurelian.agents.gocam.gocam_tools import (
    search_gocams as search,
    lookup_gocam,
    lookup_uniprot_entry
)
from aurelian.agents.literature.literature_tools import (
    lookup_pmid,
    search_literature_web as search_web,
    retrieve_literature_page as retrieve_web_page
)
from aurelian.agents.gocam.gocam_gradio import ui, chat

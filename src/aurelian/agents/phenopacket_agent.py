"""
DEPRECATED: This module has been refactored into the phenopackets/ subdirectory.

This file remains for backward compatibility, but you should use:
- aurelian.agents.phenopackets.phenopackets_agent
- aurelian.agents.phenopackets.phenopackets_config
- aurelian.agents.phenopackets.phenopackets_tools
- aurelian.agents.phenopackets.phenopackets_gradio
"""

# Re-export from new location
from aurelian.agents.phenopackets.phenopackets_agent import phenopackets_agent
from aurelian.agents.phenopackets.phenopackets_config import PhenopacketsDependencies
from aurelian.agents.phenopackets.phenopackets_tools import (
    search_phenopackets as search,
    lookup_phenopacket,
    lookup_pmid,
    search_web,
    retrieve_web_page
)
from aurelian.agents.phenopackets.phenopackets_gradio import chat

"""
UniProt agent package for interacting with the UniProt database.
"""

from .uniprot_agent import uniprot_agent, UNIPROT_SYSTEM_PROMPT
from .uniprot_config import UniprotConfig, get_config
from .uniprot_gradio import chat
from .uniprot_mcp import (
    get_uniprot_mcp_tools,
    get_uniprot_mcp_messages,
    handle_uniprot_mcp_request,
)
from .uniprot_tools import lookup_uniprot_entry, search, uniprot_mapping, normalize_uniprot_id

__all__ = [
    # Agent
    "uniprot_agent",
    "UNIPROT_SYSTEM_PROMPT",
    
    # Config
    "UniprotConfig",
    "get_config",
    
    # Tools
    "lookup_uniprot_entry",
    "search",
    "uniprot_mapping",
    "normalize_uniprot_id",
    
    # Gradio
    "chat",
    
    # MCP
    "get_uniprot_mcp_tools",
    "get_uniprot_mcp_messages",
    "handle_uniprot_mcp_request",
]
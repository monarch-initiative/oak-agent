"""
Ubergraph agent package for working with ontologies via the UberGraph endpoint.
"""

from .ubergraph_agent import (
    ubergraph_agent, 
    ASSUMPTIONS,
    add_ontology_assumptions,
    add_prefixes,
)
from .ubergraph_config import Dependencies, DEFAULT_PREFIXES, get_config
from .ubergraph_gradio import chat
from .ubergraph_tools import (
    query_ubergraph,
    QueryResults,
    simplify_value,
    simplify_results,
)

__all__ = [
    # Agent
    "ubergraph_agent",
    "ASSUMPTIONS",
    "add_ontology_assumptions",
    "add_prefixes",
    
    # Config
    "Dependencies",
    "DEFAULT_PREFIXES",
    "get_config",
    
    # Tools
    "query_ubergraph",
    "QueryResults",
    "simplify_value",
    "simplify_results",
    
    # Gradio
    "chat",
]
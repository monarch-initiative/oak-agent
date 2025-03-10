"""
Agent for working with ontologies via UberGraph endpoint - DEPRECATED

This module is maintained for backward compatibility.
Please use aurelian.agents.ubergraph.ubergraph_agent instead.
"""

from aurelian.agents.ubergraph.ubergraph_agent import (
    ubergraph_agent,
    ASSUMPTIONS,
    add_ontology_assumptions,
    add_prefixes,
)
from aurelian.agents.ubergraph.ubergraph_config import Dependencies, DEFAULT_PREFIXES
from aurelian.agents.ubergraph.ubergraph_gradio import chat
from aurelian.agents.ubergraph.ubergraph_tools import (
    query_ubergraph,
    QueryResults,
    simplify_value,
    simplify_results,
)

__all__ = [
    "ubergraph_agent",
    "ASSUMPTIONS",
    "add_ontology_assumptions",
    "add_prefixes",
    "Dependencies",
    "DEFAULT_PREFIXES",
    "chat",
    "query_ubergraph",
    "QueryResults",
    "simplify_value",
    "simplify_results",
]
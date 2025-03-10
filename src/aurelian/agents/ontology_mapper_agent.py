"""
Agent for creating ontology mappings - DEPRECATED

This module is maintained for backward compatibility.
Please use aurelian.agents.ontology_mapper.ontology_mapper_agent instead.
"""

from aurelian.agents.ontology_mapper.ontology_mapper_agent import (
    ontology_mapper_agent,
    add_ontologies,
)
from aurelian.agents.ontology_mapper.ontology_mapper_config import OntologyMapperDependencies
from aurelian.agents.ontology_mapper.ontology_mapper_gradio import chat
from aurelian.agents.ontology_mapper.ontology_mapper_tools import (
    search_terms, 
    search_web,
    retrieve_web_page,
    get_ontology_adapter,
)

__all__ = [
    "ontology_mapper_agent",
    "add_ontologies",
    "OntologyMapperDependencies",
    "search_terms",
    "search_web",
    "retrieve_web_page",
    "get_ontology_adapter",
    "chat",
]
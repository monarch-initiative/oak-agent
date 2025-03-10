"""
Gradio interface for the Ontology Mapper agent.
"""
import os
from typing import List, Optional

import gradio as gr

from aurelian.utils.async_utils import run_sync
from .ontology_mapper_agent import ontology_mapper_agent
from .ontology_mapper_config import OntologyMapperDependencies, get_config


def chat(deps: Optional[OntologyMapperDependencies] = None, **kwargs):
    """
    Initialize a chat interface for the Ontology Mapper agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = get_config()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: ontology_mapper_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Ontology Mapper AI Assistant",
        examples=[
            "Find the term in the cell ontology for neuron",
            "Best terms to use for the middle 3 fingers",
            "What is the term for the process of cell division in GO?",
            """
            Find good MP terms for the following. If no matches can be found, suggest appropriate action

            * CA1 TBS Reduced
            * CA1 TBS Increased
            * Surface righting Reduced
            * Contextual fear conditioning (shock context/context shock) Reduced
            * Morris water maze Reduced
            * Rotarod Increased
            * Rotarod Reduced
            """,
        ]
    )
"""
Gradio interface for the UberGraph agent.
"""
import os
from typing import List, Optional

import gradio as gr

from aurelian.utils.async_utils import run_sync
from .ubergraph_agent import ubergraph_agent
from .ubergraph_config import Dependencies, get_config


def chat(deps: Optional[Dependencies] = None, **kwargs):
    """
    Initialize a chat interface for the UberGraph agent.
    
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
        result = run_sync(lambda: ubergraph_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="UberGraph SPARQL Assistant",
        examples=[
            "Find all cell types that are part of the heart",
            "What is the definition of CL:0000746?",
            "What genes are expressed in neurons?",
            "What are the subclasses of skeletal muscle tissue?",
        ]
    )
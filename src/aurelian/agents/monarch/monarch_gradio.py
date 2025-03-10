"""
Gradio interface for the Monarch agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.utils.async_utils import run_sync
from .monarch_agent import monarch_agent
from .monarch_config import MonarchDependencies


def chat(taxon: Optional[str] = None, **kwargs):
    """
    Initialize a chat interface for the Monarch agent.
    
    Args:
        taxon: Optional taxon ID to use, defaults to human (9606)
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = MonarchDependencies()
    if taxon:
        deps.taxon = taxon

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: monarch_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Monarch Knowledge Base AI Assistant",
        examples=[
            ["Find associations for gene BRCA1"],
            ["What diseases are associated with the APOE gene?"],
            ["Find information about disease MONDO:0007254"],
            ["What genes are associated with Alzheimer's disease?"]
        ]
    )
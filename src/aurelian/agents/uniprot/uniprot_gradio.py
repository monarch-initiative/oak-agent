"""
Gradio interface for the UniProt agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.uniprot.uniprot_agent import uniprot_agent
from aurelian.agents.uniprot.uniprot_config import UniprotConfig
from aurelian.utils.async_utils import run_sync


def chat(**kwargs):
    """
    Initialize a chat interface for the UniProt agent.
    
    Args:
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = UniprotConfig()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: uniprot_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="UniProt AI Assistant",
        examples=[
            ["Search for human insulin protein"],
            ["Look up UniProt entry P01308"],
            ["Map UniProt IDs P01308,P01009 to PDB database"],
            ["What domains are present in UniProt entry P53_HUMAN?"],
            ["Find all proteins related to Alzheimer's disease"]
        ]
    )
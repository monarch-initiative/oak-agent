"""
Gradio UI for the AmiGO agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.amigo.amigo_agent import amigo_agent
from aurelian.agents.amigo.amigo_config import AmiGODependencies
from aurelian.utils.async_utils import run_sync


def chat(taxon: Optional[str] = None, **kwargs):
    """
    Initialize a chat interface for the AmiGO agent.
    
    Args:
        taxon: Optional NCBI Taxonomy ID, defaults to human (9606)
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = AmiGODependencies()
    if taxon:
        deps.taxon = taxon

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: amigo_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="AmiGO AI Assistant",
        examples=[
            ["What are some annotations for the protein UniProtKB:Q9UMS5"],
            ["Check PMID:19661248 for over-annotation"],
            ["What genes are involved in the ribosome biogenesis pathway?"],
            ["Map UniProtKB:P04637 to KEGG database"],
            ["Search for genes involved in DNA repair and show me their annotations"]
        ]
    )
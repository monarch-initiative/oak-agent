"""
Gradio UI for the chemistry agent.
"""
from typing import List

import gradio as gr

from aurelian.agents.chemistry.chemistry_agent import chemistry_agent
from aurelian.agents.chemistry.chemistry_config import ChemistryDependencies
from aurelian.utils.async_utils import run_sync


def chat(workdir: str = None, **kwargs):
    """
    Initialize a chat interface for the chemistry agent.
    
    Args:
        workdir: Optional working directory path
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = ChemistryDependencies()
    if workdir:
        deps.workdir.location = workdir

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: chemistry_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Chemistry AI Assistant",
        examples=[
            ["Explain the structure of caffeine (CHEBI:27732)"],
            ["What does the structure of aspirin (CHEBI:15365) tell us about its properties?"],
            ["Interpret this SMILES: CC(=O)OC1=CC=CC=C1C(=O)O"]
        ]
    )
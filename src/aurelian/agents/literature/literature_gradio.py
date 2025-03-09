"""
Gradio UI for the literature agent.
"""
from typing import List

import gradio as gr

from aurelian.agents.literature.literature_agent import literature_agent
from aurelian.agents.literature.literature_config import LiteratureDependencies
from aurelian.utils.async_utils import run_sync


def chat(workdir: str = None, **kwargs):
    """
    Initialize a chat interface for the literature agent.
    
    Args:
        workdir: Optional working directory path
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = LiteratureDependencies()
    if workdir:
        deps.workdir.location = workdir

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: literature_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Scientific Literature Assistant",
        examples=[
            ["Look up this article: PMID:31653696"],
            ["Find information about Alzheimer's disease genetics in recent papers"],
            ["What is the DOI for PMID:27629041?"],
            ["Get the abstract of PMID:30478089"],
            ["Convert this DOI to a PMID: 10.1038/nature12373"]
        ]
    )
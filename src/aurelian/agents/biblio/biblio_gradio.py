"""
Gradio interface for the Biblio agent.
"""
from typing import List

import gradio as gr

from .biblio_agent import biblio_agent
from .biblio_config import get_config


async def get_info(query: str, history: List[str]) -> str:
    """
    Process a query using the biblio agent.
    
    Args:
        query: The user query
        history: The conversation history
        
    Returns:
        The agent's response
    """
    print(f"QUERY: {query}")
    print(f"HISTORY: {history}")
    
    # Add history to the query if available
    if history:
        query += "## History"
        for h in history:
            query += f"\n{h}"
            
    # Initialize dependencies
    deps = get_config()
    
    # Run the agent
    result = await biblio_agent.run(query, deps=deps)
    return result.data


def chat(**kwargs):
    """
    Create a Gradio chat interface for the Biblio agent.
    
    Args:
        kwargs: Additional keyword arguments for the agent
        
    Returns:
        A Gradio ChatInterface
    """
    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Biblio AI Assistant",
        examples=[
            ["What patients have liver disease?"],
            ["What biblio involve genes from metabolic pathways"],
            ["How does the type of variant affect phenotype in peroxisomal disorders?"],
            ["Examine biblio for skeletal dysplasias, check them against publications"],
        ],
    )
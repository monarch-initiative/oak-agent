"""
Gradio interface for the RAG agent.
"""
from typing import List

import gradio as gr

from .rag_agent import rag_agent
from .rag_config import RagDependencies, get_config


async def get_info(query: str, history: List[str], deps: RagDependencies, model: str = None) -> str:
    """
    Process a query using the RAG agent.
    
    Args:
        query: The user query
        history: The conversation history
        deps: The agent dependencies
        model: Optional model override
        
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
    
    # Run the agent
    result = await rag_agent.run(query, deps=deps, model=model)
    return result.data


def chat(model=None, **kwargs):
    """
    Create a Gradio chat interface for the RAG agent.
    
    Args:
        model: Optional model override
        kwargs: Additional keyword arguments for dependencies
        
    Returns:
        A Gradio ChatInterface
    """
    # Initialize dependencies
    deps = get_config(**kwargs) if kwargs else RagDependencies(**kwargs)
    
    def get_info_wrapper(query: str, history: List[str]) -> str:
        """Wrapper for the async get_info function."""
        import asyncio
        return asyncio.run(get_info(query, history, deps, model))
    
    return gr.ChatInterface(
        fn=get_info_wrapper,
        type="messages",
        title="RAG AI Assistant",
        examples=[
            ["What papers in collection are relevant to microbial nitrogen fixation?"],
        ],
    )
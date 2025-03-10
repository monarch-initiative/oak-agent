"""
Gradio interface for the Checklist agent.
"""
from typing import List

import gradio as gr

from .checklist_agent import checklist_agent
from .checklist_config import get_config


async def get_info(query: str, history: List[str]) -> str:
    """
    Process a query using the checklist agent.
    
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
    result = await checklist_agent.run(query, deps=deps)
    return result.data


def chat(**kwargs):
    """
    Create a Gradio chat interface for the Checklist agent.
    
    Returns:
        A Gradio ChatInterface
    """
    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Checklist AI Assistant",
        examples=[
            ["Evaluate https://journals.asm.org/doi/10.1128/mra.01361-19 using STREAMS"],
            [
                (
                    "Check the paper 'Exploration of the Biosynthetic Potential of the Populus Microbiome'"
                    " https://journals.asm.org/doi/10.1128/msystems.00045-18"
                )
            ],
        ],
    )
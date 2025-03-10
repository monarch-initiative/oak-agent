"""
Gradio interface for the Diagnosis agent.
"""
import os
from typing import List, Optional

import gradio as gr

from aurelian.utils.async_utils import run_sync
from .diagnosis_agent import diagnosis_agent
from .diagnosis_config import DiagnosisDependencies, get_config


def chat(deps: Optional[DiagnosisDependencies] = None, **kwargs):
    """
    Initialize a chat interface for the Diagnosis agent.
    
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
        result = run_sync(lambda: diagnosis_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Diagnosis AI Assistant",
        examples=[
            """Patient has growth failure, distinct facial features, alopecia, and skin aging.
            Findings excluded: Pigmented nevi, cafe-au-lait spots, and photosensitivity.
            Onset was in infancy.
            Return diagnosis with MONDO ID""",
            "What eye phenotypes does Marfan syndrome have?",
            "What is the ID for Ehlers-Danlos syndrome type 1?",
            "What are the kinds of Ehlers-Danlos syndrome?",
            "Look at phenotypes for Ehlers-Danlos classic type 2. Do a literature search to look at latest studies. What is missing from the KB?",
        ],
    )
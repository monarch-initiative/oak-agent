"""
Gradio UI for the GOCAM agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.gocam.gocam_agent import gocam_agent
from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.utils.async_utils import run_sync


def ui():
    """
    Initialize a basic interface for the GOCAM agent (non-chat).
    
    Returns:
        A Gradio interface
    """
    deps = GOCAMDependencies()

    def get_info(query: str):
        print(f"QUERY: {query}")
        result = run_sync(lambda: gocam_agent.run_sync(query, deps=deps))
        return result.data

    demo = gr.Interface(
        fn=get_info,
        inputs=gr.Textbox(
            label="Ask about any GO-CAMs", placeholder="What is the function of caspase genes in apoptosis pathways?"
        ),
        outputs=gr.Textbox(label="GO-CAM Information"),
        title="GO-CAM AI Assistant",
        description="Ask me anything about GO-CAMs and I will try to provide you with the information you need.",
    )
    return demo


def chat(db_path: Optional[str] = None, collection_name: Optional[str] = None, **kwargs):
    """
    Initialize a chat interface for the GOCAM agent.
    
    Args:
        db_path: Optional database path, defaults to MongoDB localhost
        collection_name: Optional collection name, defaults to "main"
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = GOCAMDependencies()
    if db_path:
        deps.db_path = db_path
    if collection_name:
        deps.collection_name = collection_name

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: gocam_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="GO-CAM AI Assistant",
        examples=[
            ["What is the function of caspase genes in apoptosis pathways?"],
            ["What models involve autophagy?"],
            [
                (
                    "find the wikipedia article on the integrated stress response pathway,"
                    " download it, and summarize the genes and what they do."
                    " then find similar GO-CAMs, look up their details,"
                    " and compare them to the reviews"
                )
            ],
            ["Find models involving the NLRP3 inflammasome. Compare the GO-CAM model with information available from uniprot"],
            ["Examine models for antimicrobial resistance, look for commonalities in genes"],
        ],
    )
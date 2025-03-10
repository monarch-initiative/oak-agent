"""
Gradio UI for the phenopackets agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.phenopackets.phenopackets_agent import phenopackets_agent
from aurelian.agents.phenopackets.phenopackets_config import PhenopacketsDependencies
from aurelian.utils.async_utils import run_sync


def chat(db_path: Optional[str] = None, collection_name: Optional[str] = None, **kwargs):
    """
    Initialize a chat interface for the phenopackets agent.
    
    Args:
        db_path: Optional database path, defaults to MongoDB localhost
        collection_name: Optional collection name, defaults to "main"
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    deps = PhenopacketsDependencies()
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
        result = run_sync(lambda: phenopackets_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Phenopackets AI Assistant",
        examples=[
            ["What patients have liver disease?"],
            ["What phenopackets involve genes from metabolic pathways?"],
            ["How does the type of variant affect phenotype in peroxisomal disorders?"],
            ["Examine phenopackets for skeletal dysplasias and compare their phenotypes"],
            ["Look up any patients with mutations in the PNPLA6 gene"]
        ]
    )
"""Gradio interface for the Relation Extraction Agent."""

import os
import json
import asyncio
import tempfile
import gradio as gr
import pandas as pd
from typing import Dict, List, Optional

from pydantic_ai.chat import ChatMessage

from aurelian.agents.relation_extraction.relation_extraction_agent import relation_extraction_agent
from aurelian.agents.relation_extraction.relation_extraction_config import RelationExtractionDependencies

# Global state for the Gradio app
class AppState:
    def __init__(self):
        self.pdf_directory = None
        self.cache_directory = None
        self.dependencies = None
        self.history = []
        self.current_pdfs = []
        self.extracted_relations = []

state = AppState()

async def chat_with_agent(message: str, history: List[List[str]]) -> List[List[str]]:
    """Process a message with the agent and update the chat history."""
    if not state.dependencies:
        return [], "Please set up the PDF directory first."
    
    # Add user message to history
    state.history.append(["User", message])
    
    # Process with agent
    try:
        response = await relation_extraction_agent.chat(
            messages=[ChatMessage(role="user", content=message)],
            dependencies=state.dependencies
        )
        
        # Add agent response to history
        state.history.append(["Agent", response.content])
        
        # Convert history to Gradio format
        gradio_history = [[user, assistant] for user, assistant in zip(
            [h[1] for h in state.history if h[0] == "User"],
            [h[1] for h in state.history if h[0] == "Agent"]
        )]
        
        return gradio_history, ""
    except Exception as e:
        return [[message, f"Error: {str(e)}"] for message, _ in history], str(e)


def setup_directories(pdf_dir: str, cache_dir: Optional[str] = None) -> str:
    """Set up the PDF and cache directories."""
    try:
        # Validate PDF directory
        if not os.path.exists(pdf_dir):
            return f"Error: PDF directory '{pdf_dir}' does not exist."
        
        # Use specified cache directory or create a default one
        final_cache_dir = cache_dir if cache_dir else os.path.join(pdf_dir, ".relation_extraction_cache")
        
        # Create dependencies
        state.pdf_directory = pdf_dir
        state.cache_directory = final_cache_dir
        state.dependencies = RelationExtractionDependencies(
            pdf_directory=pdf_dir,
            cache_directory=final_cache_dir
        )
        
        # Get initial list of PDFs
        pdf_files = []
        for filename in os.listdir(pdf_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(pdf_dir, filename)
                is_processed = state.dependencies.is_processed(file_path)
                pdf_files.append({
                    "file_path": file_path,
                    "filename": filename,
                    "is_processed": is_processed
                })
        
        state.current_pdfs = pdf_files
        
        return f"Successfully set up directories. Found {len(pdf_files)} PDF files."
    except Exception as e:
        return f"Error setting up directories: {str(e)}"


def get_pdf_list() -> pd.DataFrame:
    """Get the list of PDFs as a DataFrame for display."""
    if not state.current_pdfs:
        return pd.DataFrame(columns=["Filename", "Processed"])
    
    return pd.DataFrame([
        {"Filename": pdf["filename"], "Processed": "Yes" if pdf["is_processed"] else "No"}
        for pdf in state.current_pdfs
    ])


async def process_all_pdfs() -> str:
    """Process all unprocessed PDFs in the directory."""
    if not state.dependencies:
        return "Please set up the PDF directory first."
    
    try:
        # Use the agent's tool to process all PDFs
        result = await process_all_unprocessed_pdfs(state.dependencies)
        
        # Update the PDF list
        for pdf in state.current_pdfs:
            pdf_path = pdf["file_path"]
            pdf["is_processed"] = state.dependencies.is_processed(pdf_path)
        
        # Format the result message
        if result["processed"] == 0:
            return "No new PDFs to process."
        else:
            return f"Processed {result['processed']} PDFs. Extracted {result['total_relations']} relations."
    
    except Exception as e:
        return f"Error processing PDFs: {str(e)}"


async def get_relations() -> pd.DataFrame:
    """Get all extracted relations as a DataFrame."""
    if not state.dependencies:
        return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Paper"])
    
    try:
        # Use the agent's tool to get all relations
        relations = await get_extracted_relations(state.dependencies)
        state.extracted_relations = relations
        
        if not relations:
            return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Paper"])
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "Subject": r["subject"],
                "Predicate": r["predicate"],
                "Object": r["object"],
                "Evidence": r["evidence"],
                "Paper": r.get("paper_title", "Unknown")
            }
            for r in relations
        ])
        
        return df
    
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])


def export_relations(format_type: str) -> Dict:
    """Export relations to a file in the specified format."""
    if not state.extracted_relations:
        return {"error": "No relations to export"}
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_type}") as temp_file:
            file_path = temp_file.name
        
        if format_type == "json":
            with open(file_path, 'w') as f:
                json.dump(state.extracted_relations, f, indent=2)
        elif format_type == "csv":
            df = pd.DataFrame([
                {
                    "Subject": r["subject"],
                    "Predicate": r["predicate"],
                    "Object": r["object"],
                    "Evidence": r["evidence"],
                    "Paper_DOI": r.get("paper_doi", ""),
                    "Paper_Title": r.get("paper_title", ""),
                    "Paper_Year": r.get("paper_year", ""),
                    "Confidence": r.get("confidence", 1.0)
                }
                for r in state.extracted_relations
            ])
            df.to_csv(file_path, index=False)
        
        return {"file_path": file_path}
    
    except Exception as e:
        return {"error": str(e)}


def create_demo():
    """Create the Gradio demo interface."""
    
    with gr.Blocks(title="Relation Extraction Agent") as demo:
        gr.Markdown("# Scientific Paper Relation Extraction Agent")
        gr.Markdown("Extract meaningful relations from scientific papers in PDF format.")
        
        with gr.Tab("Setup"):
            with gr.Row():
                pdf_dir_input = gr.Textbox(
                    label="PDF Directory", 
                    placeholder="Enter the full path to directory containing PDFs"
                )
                cache_dir_input = gr.Textbox(
                    label="Cache Directory (Optional)", 
                    placeholder="Leave empty for default cache location"
                )
            
            setup_button = gr.Button("Setup Directories")
            setup_output = gr.Textbox(label="Setup Result")
            
            setup_button.click(
                fn=setup_directories, 
                inputs=[pdf_dir_input, cache_dir_input], 
                outputs=setup_output
            )
        
        with gr.Tab("PDF Files"):
            pdf_refresh_button = gr.Button("Refresh PDF List")
            pdf_list = gr.DataFrame(headers=["Filename", "Processed"])
            process_button = gr.Button("Process All Unprocessed PDFs")
            process_result = gr.Textbox(label="Processing Result")
            
            pdf_refresh_button.click(fn=get_pdf_list, inputs=[], outputs=pdf_list)
            process_button.click(fn=process_all_pdfs, inputs=[], outputs=process_result)
        
        with gr.Tab("Relations"):
            get_relations_button = gr.Button("Get Extracted Relations")
            relations_table = gr.DataFrame()
            
            with gr.Row():
                export_format = gr.Radio(
                    choices=["json", "csv"], 
                    label="Export Format", 
                    value="json"
                )
                export_button = gr.Button("Export Relations")
            
            export_result = gr.JSON(label="Export Result")
            
            get_relations_button.click(fn=get_relations, inputs=[], outputs=relations_table)
            export_button.click(fn=export_relations, inputs=[export_format], outputs=export_result)
        
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Message")
            clear = gr.Button("Clear")
            chat_error = gr.Textbox(label="Error")
            
            msg.submit(chat_with_agent, [msg, chatbot], [chatbot, chat_error])
            clear.click(lambda: ([], ""), outputs=[chatbot, chat_error])
    
    return demo


# For direct execution
if __name__ == "__main__":
    demo = create_demo()
    demo.launch()
"""Gradio interface for the Relation Extraction Agent."""

import os
import json
import asyncio
import tempfile
import gradio as gr
import pandas as pd
from typing import Dict, List, Optional, Tuple

from pydantic_ai.chat import ChatMessage

from aurelian.agents.relation_extraction.relation_extraction_agent import relation_extraction_agent
from aurelian.agents.relation_extraction.relation_extraction_config import RelationExtractionDependencies
from aurelian.agents.relation_extraction.relation_extraction_tools import (
    map_all_relations_to_ontology,
    export_relations_as_rdf
)

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


async def get_relations(include_ontology: bool = False) -> pd.DataFrame:
    """
    Get all extracted relations as a DataFrame.
    
    Args:
        include_ontology: Whether to include ontology mapping information in the DataFrame
    """
    if not state.dependencies:
        return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Paper"])
    
    try:
        # Use the agent's tool to get all relations
        relations = await get_extracted_relations(state.dependencies)
        state.extracted_relations = relations
        
        if not relations:
            return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Paper"])
        
        # Prepare columns based on whether to include ontology info
        if include_ontology:
            # Convert to DataFrame with ontology information
            df = pd.DataFrame([
                {
                    "Subject": r["subject"],
                    "Subject_Ontology": f"{r.get('subject_ontology_id', '')} ({r.get('subject_ontology_source', '')})" if r.get('subject_ontology_id') else "",
                    "Predicate": r["predicate"],
                    "Predicate_Ontology": f"{r.get('predicate_ontology_id', '')} ({r.get('predicate_ontology_source', '')})" if r.get('predicate_ontology_id') else "",
                    "Object": r["object"],
                    "Object_Ontology": f"{r.get('object_ontology_id', '')} ({r.get('object_ontology_source', '')})" if r.get('object_ontology_id') else "",
                    "Evidence": r["evidence"],
                    "Paper": r.get("paper_title", "Unknown"),
                    "DOI": r.get("paper_doi", "")
                }
                for r in relations
            ])
        else:
            # Simple version without ontology information
            df = pd.DataFrame([
                {
                    "Subject": r["subject"],
                    "Predicate": r["predicate"],
                    "Object": r["object"],
                    "Evidence": r["evidence"],
                    "Paper": r.get("paper_title", "Unknown"),
                    "DOI": r.get("paper_doi", "")
                }
                for r in relations
            ])
        
        return df
    
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])


async def map_ontologies() -> Dict:
    """Map all relations to ontology terms."""
    if not state.dependencies:
        return {"status": "error", "message": "Please set up the PDF directory first."}
    
    try:
        # Use the agent's tool to map relations to ontology terms
        result = await map_all_relations_to_ontology(state.dependencies)
        return result
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def export_relations(format_type: str) -> Dict:
    """Export relations to a file in the specified format."""
    if not state.dependencies or not state.extracted_relations:
        return {"error": "No relations to export"}
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_type}") as temp_file:
            file_path = temp_file.name
        
        if format_type == "json":
            with open(file_path, 'w') as f:
                json.dump(state.extracted_relations, f, indent=2)
                
        elif format_type == "csv":
            # Include ontology information in the CSV
            df = pd.DataFrame([
                {
                    "Subject": r["subject"],
                    "Subject_Ontology_ID": r.get("subject_ontology_id", ""),
                    "Subject_Ontology_Source": r.get("subject_ontology_source", ""),
                    
                    "Predicate": r["predicate"],
                    "Predicate_Ontology_ID": r.get("predicate_ontology_id", ""),
                    "Predicate_Ontology_Source": r.get("predicate_ontology_source", ""),
                    
                    "Object": r["object"],
                    "Object_Ontology_ID": r.get("object_ontology_id", ""),
                    "Object_Ontology_Source": r.get("object_ontology_source", ""),
                    
                    "Evidence": r["evidence"],
                    "Confidence": r.get("confidence", 1.0),
                    "Paper_DOI": r.get("paper_doi", ""),
                    "Paper_Title": r.get("paper_title", ""),
                    "Paper_Year": r.get("paper_year", ""),
                    "Paper_PMID": r.get("paper_pmid", ""),
                    "Section": r.get("section", ""),
                    "Extraction_Date": r.get("extraction_date", "")
                }
                for r in state.extracted_relations
            ])
            df.to_csv(file_path, index=False)
            
        elif format_type == "rdf":
            # Use the agent's tool to export as RDF
            result = await export_relations_as_rdf(state.dependencies, file_path)
            if result.get("status") != "success":
                return result
        
        return {"status": "success", "file_path": file_path}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_demo():
    """Create the Gradio demo interface."""
    
    with gr.Blocks(title="Relation Extraction Agent") as demo:
        gr.Markdown("# Scientific Paper Relation Extraction Agent")
        gr.Markdown("Extract meaningful relations from scientific papers in PDF format and map them to ontology terms.")
        
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
            with gr.Row():
                get_relations_button = gr.Button("Get Extracted Relations")
                include_ontology = gr.Checkbox(label="Include Ontology Mappings", value=False)
            
            relations_table = gr.DataFrame()
            
            get_relations_button.click(
                fn=get_relations, 
                inputs=[include_ontology], 
                outputs=relations_table
            )
        
        with gr.Tab("Ontology Mapping"):
            map_ontology_button = gr.Button("Map Relations to Ontology Terms")
            mapping_result = gr.JSON(label="Mapping Result")
            
            map_ontology_button.click(fn=map_ontologies, inputs=[], outputs=mapping_result)
            
            gr.Markdown("### Ontology Mapping Details")
            gr.Markdown("""
            The mapping process connects extracted terms to standard ontologies:
            - Gene Ontology (GO) for biological processes, cellular components, molecular functions
            - ChEBI for chemical entities 
            - Disease Ontology (DOID) for diseases
            - Protein Ontology (PR) for proteins
            - Uberon for anatomical entities
            - Relation Ontology (RO) for relationship types
            """)
        
        with gr.Tab("Export"):
            with gr.Row():
                export_format = gr.Radio(
                    choices=["json", "csv", "rdf"], 
                    label="Export Format", 
                    value="json"
                )
                export_button = gr.Button("Export Relations")
            
            export_result = gr.JSON(label="Export Result")
            
            gr.Markdown("### Export Format Details")
            gr.Markdown("""
            - **JSON**: Full relation data including ontology mappings and all metadata
            - **CSV**: Tabular format with separate columns for entities and their ontology mappings
            - **RDF**: Semantic web format using standard ontology URIs with full provenance
            """)
            
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
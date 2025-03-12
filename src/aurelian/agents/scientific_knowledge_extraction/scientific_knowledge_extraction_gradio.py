"""Gradio interface for the Scientific Knowledge Extraction Agent."""

import os
import json
import asyncio
import tempfile
import gradio as gr
import pandas as pd
from typing import Dict, List, Optional, Tuple

# Importing only the agent, will use dict for messages
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_agent import scientific_knowledge_extraction_agent
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    map_all_assertions_to_ontology,
    export_assertions_as_rdf,
    process_all_unprocessed_pdfs,
    get_extracted_knowledge
)

# Global state for the Gradio app
class AppState:
    def __init__(self):
        self.pdf_directory = None
        self.cache_directory = None
        self.dependencies = None
        self.history = []
        self.current_pdfs = []
        self.extracted_knowledge = []

state = AppState()

async def chat_with_agent(message: str, history: List[List[str]]) -> List[List[str]]:
    """Process a message with the agent and update the chat history."""
    if not state.dependencies:
        return [], "Please set up the PDF directory first."
    
    # Add user message to history
    state.history.append(["User", message])
    
    # Process with agent
    try:
        response = await scientific_knowledge_extraction_agent.chat(
            messages=[{"role": "user", "content": message}],
            dependencies=state.dependencies
        )
        
        # Add agent response to history
        state.history.append(["Agent", response.content])
        
        # Convert history to Gradio messages format
        gradio_history = []
        for i in range(0, len(state.history), 2):
            if i+1 < len(state.history):
                user_msg = state.history[i][1]
                agent_msg = state.history[i+1][1]
                gradio_history.append({"role": "user", "content": user_msg})
                gradio_history.append({"role": "assistant", "content": agent_msg})
        
        return gradio_history, ""
    except Exception as e:
        # Format the error as messages
        error_msg = f"Error: {str(e)}"
        return [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}], error_msg


def setup_directories(pdf_dir: str, cache_dir: Optional[str] = None) -> str:
    """Set up the PDF and cache directories."""
    try:
        # Validate PDF directory
        if not os.path.exists(pdf_dir):
            return f"Error: PDF directory '{pdf_dir}' does not exist."
        
        # Use specified cache directory or create a default one
        final_cache_dir = cache_dir if cache_dir else os.path.join(pdf_dir, ".scientific_knowledge_cache")
        
        # Create dependencies
        state.pdf_directory = pdf_dir
        state.cache_directory = final_cache_dir
        state.dependencies = ScientificKnowledgeExtractionDependencies(
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
        # Create a RunContext for the tools
        class RunContext:
            def __init__(self, deps):
                self.dependencies = deps
                
        ctx = RunContext(state.dependencies)
        
        # Use the agent's tool to process all PDFs
        result = await process_all_unprocessed_pdfs(ctx)
        
        # Update the PDF list
        for pdf in state.current_pdfs:
            pdf_path = pdf["file_path"]
            pdf["is_processed"] = state.dependencies.is_processed(pdf_path)
        
        # Format the result message
        if result["processed"] == 0:
            return "No new PDFs to process."
        else:
            return f"Processed {result['processed']} PDFs. Extracted {result.get('total_assertions', 0)} scientific assertions."
    
    except Exception as e:
        return f"Error processing PDFs: {str(e)}"


async def get_knowledge(include_ontology: bool = False) -> pd.DataFrame:
    """
    Get all extracted scientific knowledge as a DataFrame.
    
    Args:
        include_ontology: Whether to include ontology mapping information in the DataFrame
    """
    if not state.dependencies:
        return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Paper"])
    
    try:
        # Create RunContext
        class RunContext:
            def __init__(self, deps):
                self.dependencies = deps
                
        ctx = RunContext(state.dependencies)
        
        # Use the agent's tool to get all knowledge
        knowledge = await get_extracted_knowledge(ctx)
        state.extracted_knowledge = knowledge
        
        if not knowledge:
            return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Paper"])
        
        # Prepare columns based on whether to include ontology info
        if include_ontology:
            # Convert to DataFrame with ontology information
            df = pd.DataFrame([
                {
                    "Subject": k["subject"],
                    "Subject_Ontology": f"{k.get('subject_ontology_id', '')} ({k.get('subject_ontology_source', '')})" if k.get('subject_ontology_id') else "",
                    "Predicate": k["predicate"],
                    "Predicate_Ontology": f"{k.get('predicate_ontology_id', '')} ({k.get('predicate_ontology_source', '')})" if k.get('predicate_ontology_id') else "",
                    "Object": k["object"],
                    "Object_Ontology": f"{k.get('object_ontology_id', '')} ({k.get('object_ontology_source', '')})" if k.get('object_ontology_id') else "",
                    "Evidence": k["evidence"],
                    "Paper": k.get("paper_title", "Unknown"),
                    "DOI": k.get("paper_doi", "")
                }
                for k in knowledge
            ])
        else:
            # Simple version without ontology information
            df = pd.DataFrame([
                {
                    "Subject": k["subject"],
                    "Predicate": k["predicate"],
                    "Object": k["object"],
                    "Evidence": k["evidence"],
                    "Paper": k.get("paper_title", "Unknown"),
                    "DOI": k.get("paper_doi", "")
                }
                for k in knowledge
            ])
        
        return df
    
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])


async def map_ontologies() -> Dict:
    """Map all scientific assertions to ontology terms."""
    if not state.dependencies:
        return {"status": "error", "message": "Please set up the PDF directory first."}
    
    try:
        # Create RunContext
        class RunContext:
            def __init__(self, deps):
                self.dependencies = deps
                
        ctx = RunContext(state.dependencies)
        
        # Use the agent's tool to map assertions to ontology terms
        result = await map_all_assertions_to_ontology(ctx)
        return result
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def export_knowledge(format_type: str) -> Dict:
    """Export scientific knowledge to a file in the specified format."""
    if not state.dependencies or not state.extracted_knowledge:
        return {"error": "No knowledge to export"}
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_type}") as temp_file:
            file_path = temp_file.name
        
        if format_type == "json":
            with open(file_path, 'w') as f:
                json.dump(state.extracted_knowledge, f, indent=2)
                
        elif format_type == "csv":
            # Include ontology information in the CSV
            df = pd.DataFrame([
                {
                    "Subject": k["subject"],
                    "Subject_Ontology_ID": k.get("subject_ontology_id", ""),
                    "Subject_Ontology_Source": k.get("subject_ontology_source", ""),
                    
                    "Predicate": k["predicate"],
                    "Predicate_Ontology_ID": k.get("predicate_ontology_id", ""),
                    "Predicate_Ontology_Source": k.get("predicate_ontology_source", ""),
                    
                    "Object": k["object"],
                    "Object_Ontology_ID": k.get("object_ontology_id", ""),
                    "Object_Ontology_Source": k.get("object_ontology_source", ""),
                    
                    "Evidence": k["evidence"],
                    "Confidence": k.get("confidence", 1.0),
                    "Paper_DOI": k.get("paper_doi", ""),
                    "Paper_Title": k.get("paper_title", ""),
                    "Paper_Year": k.get("paper_year", ""),
                    "Paper_PMID": k.get("paper_pmid", ""),
                    "Section": k.get("section", ""),
                    "Extraction_Date": k.get("extraction_date", "")
                }
                for k in state.extracted_knowledge
            ])
            df.to_csv(file_path, index=False)
            
        elif format_type == "rdf":
            # Create RunContext
            class RunContext:
                def __init__(self, deps):
                    self.dependencies = deps
                    
            ctx = RunContext(state.dependencies)
            
            # Use the agent's tool to export as RDF
            result = await export_assertions_as_rdf(ctx, file_path)
            if result.get("status") != "success":
                return result
        
        return {"status": "success", "file_path": file_path}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_demo():
    """Create the Gradio demo interface."""
    
    with gr.Blocks(title="Scientific Knowledge Extraction Agent") as demo:
        gr.Markdown("# Scientific Knowledge Extraction Agent")
        gr.Markdown("Extract and normalize scientific knowledge from research papers in PDF format.")
        
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
        
        with gr.Tab("Knowledge"):
            with gr.Row():
                get_knowledge_button = gr.Button("Get Extracted Knowledge")
                include_ontology = gr.Checkbox(label="Include Ontology Mappings", value=False)
            
            knowledge_table = gr.DataFrame()
            
            get_knowledge_button.click(
                fn=get_knowledge, 
                inputs=[include_ontology], 
                outputs=knowledge_table
            )
        
        with gr.Tab("Ontology Mapping"):
            map_ontology_button = gr.Button("Map Knowledge to Ontology Terms")
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
                export_button = gr.Button("Export Knowledge")
            
            export_result = gr.JSON(label="Export Result")
            
            gr.Markdown("### Export Format Details")
            gr.Markdown("""
            - **JSON**: Full knowledge data including ontology mappings and all metadata
            - **CSV**: Tabular format with separate columns for entities and their ontology mappings
            - **RDF**: Semantic web format using standard ontology URIs with full provenance
            """)
            
            export_button.click(fn=export_knowledge, inputs=[export_format], outputs=export_result)
        
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot(type="messages")
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
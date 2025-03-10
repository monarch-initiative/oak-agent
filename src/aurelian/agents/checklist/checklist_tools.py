"""
Tools for the Checklist agent.
"""
import asyncio
from typing import Dict
import yaml

from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.pubmed_utils import get_doi_text, get_pmid_text
from . import CONTENT_DIR, CONTENT_METADATA_PATH
from .checklist_config import ChecklistDependencies


def all_checklists() -> Dict:
    """
    Get all available checklists.
    
    Returns:
        Dictionary of all available checklists
    """
    with open(CONTENT_METADATA_PATH) as f:
        return yaml.safe_load(f)


async def retrieve_text_from_pmid(
    ctx: RunContext[ChecklistDependencies], 
    pmid: str
) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    Args:
        ctx: The run context
        pmid: The PubMed ID to look up
    
    Returns: 
        Full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    
    try:
        # Execute the potentially blocking operation in a thread pool
        text = await asyncio.to_thread(get_pmid_text, pmid)
        
        if not text or text.strip() == "":
            raise ModelRetry(f"No text found for PMID: {pmid}")
            
        return text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving text from PMID: {str(e)}")


async def retrieve_text_from_doi(
    ctx: RunContext[ChecklistDependencies], 
    doi: str
) -> str:
    """
    Lookup the text of a DOI.

    Args:
        ctx: The run context
        doi: The DOI to look up
    
    Returns: 
        Full text if available, otherwise abstract
    """
    print(f"LOOKUP DOI: {doi}")
    
    try:
        # Execute the potentially blocking operation in a thread pool
        text = await asyncio.to_thread(get_doi_text, doi)
        
        if not text or text.strip() == "":
            raise ModelRetry(f"No text found for DOI: {doi}")
            
        return text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving text from DOI: {str(e)}")


async def fetch_checklist(
    ctx: RunContext[ChecklistDependencies], 
    checklist_id: str
) -> str:
    """
    Lookup the checklist entry for a given checklist accession number.

    Args:
        ctx: The run context
        checklist_id: The checklist ID (e.g. STREAM, STORMS, ARRIVE)
    
    Returns:
        The content of the checklist
    """
    try:
        # Execute the potentially blocking operation in a thread pool
        meta = all_checklists()
        
        # Normalize and find the checklist
        selected_checklist = None
        checklist_id_lower = checklist_id.lower()
        
        for checklist in meta["checklists"]:
            if checklist["id"].lower() == checklist_id_lower:
                selected_checklist = checklist
                break
            if checklist["title"].lower() == checklist_id_lower:
                selected_checklist = checklist
                break
                
        if not selected_checklist:
            available_checklists = ", ".join([c["id"] for c in meta["checklists"]])
            raise ModelRetry(
                f"Could not find checklist with ID {checklist_id}. "
                f"Available checklists: {available_checklists}"
            )
            
        # Get the checklist file
        id = selected_checklist["id"]
        path = CONTENT_DIR / f"{id}.csv"
        
        if not path.exists():
            raise ModelRetry(f"Checklist file not found: {path}")
            
        # Read the checklist file
        with open(path) as f:
            content = f.read()
            
        if not content or content.strip() == "":
            raise ModelRetry(f"Checklist file is empty: {path}")
            
        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error fetching checklist: {str(e)}")
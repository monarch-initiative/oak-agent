"""
Tools for interacting with the Monarch Knowledge Base.
"""
import asyncio
from typing import Dict, List, Optional

from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.data_utils import obj_to_dict
from aurelian.utils.async_utils import run_sync
from .monarch_config import MonarchDependencies, get_config


def get_gene_id(ctx: RunContext[MonarchDependencies], gene_term: str) -> str:
    """
    Normalize a gene identifier.
    
    Args:
        ctx: Run context with dependencies
        gene_term: The gene term to normalize
        
    Returns:
        Normalized gene ID
    """
    # Currently just a pass-through, but could be enhanced with ID normalization
    return gene_term


async def find_gene_associations(ctx: RunContext[MonarchDependencies], gene_id: str) -> List[Dict]:
    """
    Find associations for a given gene ID.
    
    Args:
        ctx: Run context with dependencies
        gene_id: The gene ID to find associations for
        
    Returns:
        List of associations for the gene
    """
    config = ctx.deps or get_config()
    adapter = config.get_monarch_adapter()
    
    try:
        normalized_gene_id = get_gene_id(ctx, gene_id)
        
        # Execute the potentially blocking operation in a thread pool
        associations = await asyncio.to_thread(adapter.associations, [normalized_gene_id])
        
        if not associations:
            raise ModelRetry(f"No gene associations found for {gene_id}. Try a different gene identifier.")
        
        # Convert associations to dictionaries asynchronously 
        result = []
        for assoc in associations:
            dict_assoc = await asyncio.to_thread(obj_to_dict, assoc)
            result.append(dict_assoc)
            
        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving gene associations: {str(e)}")


def get_disease_id(ctx: RunContext[MonarchDependencies], term: str) -> str:
    """
    Normalize a disease identifier.
    
    Args:
        ctx: Run context with dependencies
        term: The disease term to normalize
        
    Returns:
        Normalized disease ID
    """
    # Currently just a pass-through, but could be enhanced with ID normalization
    return term


async def find_disease_associations(ctx: RunContext[MonarchDependencies], disease_id: str) -> List[Dict]:
    """
    Find associations for a given disease ID.
    
    Args:
        ctx: Run context with dependencies
        disease_id: The disease ID to find associations for
        
    Returns:
        List of associations for the disease
    """
    config = ctx.deps or get_config()
    adapter = config.get_monarch_adapter()
    
    try:
        normalized_disease_id = get_disease_id(ctx, disease_id)
        
        # Execute the potentially blocking operation in a thread pool
        associations = await asyncio.to_thread(adapter.associations, [normalized_disease_id])
        
        if not associations:
            raise ModelRetry(f"No disease associations found for {disease_id}. Try a different disease identifier.")
            
        # Convert associations to dictionaries asynchronously
        result = []
        for assoc in associations:
            dict_assoc = await asyncio.to_thread(obj_to_dict, assoc)
            result.append(dict_assoc)
            
        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving disease associations: {str(e)}")
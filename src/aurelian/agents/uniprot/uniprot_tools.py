"""
Tools for interacting with the UniProt database.
"""
from typing import Dict, List, Optional

from pydantic_ai import RunContext, ModelRetry

from .uniprot_config import UniprotConfig, get_config


def normalize_uniprot_id(uniprot_id: str) -> str:
    """Normalize a Uniprot ID by removing any version number.

    Args:
        uniprot_id: The Uniprot ID

    Returns:
        The normalized Uniprot ID
    """
    if ":" in uniprot_id:
        return uniprot_id.split(":")[-1]
    return uniprot_id


def search(ctx: RunContext[UniprotConfig], query: str) -> str:
    """Search UniProt with a query string.

    Args:
        ctx: The run context with access to the config
        query: The search query

    Returns:
        The search results in TSV format
    """
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        results = u.search(query, frmt="tsv", columns="accession,id,gene_names")
        if not results or results.strip() == "":
            raise ModelRetry(f"No results found for query: {query}")
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching UniProt: {str(e)}")


def lookup_uniprot_entry(ctx: RunContext[UniprotConfig], uniprot_acc: str) -> str:
    """Lookup the Uniprot entry for a given Uniprot accession number.

    Args:
        ctx: The run context with access to the config
        uniprot_acc: The Uniprot accession

    Returns:
        The UniProt entry in text format
    """
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        uniprot_acc = normalize_uniprot_id(uniprot_acc)
        result = u.retrieve(uniprot_acc, frmt="txt")
        if not result or result.strip() == "":
            raise ModelRetry(f"No entry found for accession: {uniprot_acc}")
        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error looking up UniProt entry: {str(e)}")


def uniprot_mapping(
    ctx: RunContext[UniprotConfig], 
    target_database: str, 
    uniprot_accs: List[str]
) -> Dict:
    """Perform a mapping of Uniprot accessions to another database.

    Args:
        ctx: The run context with access to the config
        target_database: The target database (e.g., KEGG, PDB)
        uniprot_accs: The Uniprot accessions

    Returns:
        A dictionary mapping UniProt accessions to entries in the target database
    """
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        if not uniprot_accs:
            raise ModelRetry("No UniProt accessions provided for mapping")
            
        normalized_accs = [normalize_uniprot_id(x) for x in uniprot_accs]
        result = u.mapping("UniProtKB_AC-ID", target_database, ",".join(normalized_accs))
        
        if not result:
            raise ModelRetry(f"No mappings found for accessions to {target_database}")
        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error mapping UniProt entries: {str(e)}")
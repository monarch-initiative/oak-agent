"""
MCP tools for interacting with GO KnowledgeBase via AmiGO solr endpoint.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

from aurelian.agents.amigo.amigo_agent import SYSTEM
import aurelian.agents.amigo.amigo_tools as at
from aurelian.agents.amigo.amigo_config import AmiGODependencies
from aurelian.agents.literature.literature_tools import (
    lookup_pmid as lit_lookup_pmid, 
    search_literature_web, 
    retrieve_literature_page
)
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("amigo", instructions=SYSTEM)


from aurelian.dependencies.workdir import WorkDir

def deps() -> AmiGODependencies:
    deps = AmiGODependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    
    # Get taxonomy ID from environment variable if available
    taxon = os.getenv("AMIGO_TAXON")
    if taxon:
        deps.taxon = taxon
        
    return deps

def ctx() -> RunContext[AmiGODependencies]:
    rc: RunContext[AmiGODependencies] = RunContext[AmiGODependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def find_gene_associations(gene_id: str) -> List[Dict]:
    """
    Find gene associations for a given gene or gene product.
    
    Args:
        gene_id: Gene or gene product IDs
        
    Returns:
        List[Dict]: List of gene associations
    """
    return await at.find_gene_associations(ctx(), gene_id)


@mcp.tool()
async def find_gene_associations_for_pmid(pmid: str) -> List[Dict]:
    """
    Find gene associations for a given PubMed ID.
    
    Args:
        pmid: The PubMed ID
        
    Returns:
        List[Dict]: List of gene associations for the PubMed ID
    """
    return await at.find_gene_associations_for_pmid(ctx(), pmid)


@mcp.tool()
async def lookup_uniprot_entry(uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number.
    
    Args:
        uniprot_acc: The Uniprot accession
        
    Returns:
        str: The Uniprot entry text
    """
    return await at.lookup_uniprot_entry(ctx(), uniprot_acc)


@mcp.tool()
async def uniprot_mapping(target_database: str, uniprot_accs: List[str]) -> Dict:
    """
    Perform a mapping of Uniprot accessions to another database.
    
    Args:
        target_database: The target database (e.g KEGG, PDB)
        uniprot_accs: The Uniprot accessions
        
    Returns:
        Dict: Mapping results
    """
    return await at.uniprot_mapping(ctx(), target_database, uniprot_accs)


@mcp.tool()
async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed article by its PMID.

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).

    This is useful for retrieving the full text of papers referenced in GO annotations
    to verify the evidence for gene annotations or identify potential over-annotations.
    
    Args:
        pmid: The PubMed ID to look up
        
    Returns:
        str: Full text if available, otherwise abstract
    """
    return await lit_lookup_pmid(pmid)


@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web using a text query.
    
    Args:
        query: The search query
        
    Returns:
        str: Search results with summaries
    """
    return await search_literature_web(query)


@mcp.tool()
async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.
    
    Args:
        url: The URL to fetch
        
    Returns:
        str: The contents of the web page
    """
    return await retrieve_literature_page(url)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
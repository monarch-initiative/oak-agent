"""
MCP tools for working with Gene Ontology Causal Activity Models.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.filesystem.filesystem_tools as fst
from aurelian.agents.gocam.gocam_agent import SYSTEM
import aurelian.agents.gocam.gocam_tools as gt
from aurelian.agents.literature.literature_tools import lookup_pmid as lit_lookup_pmid, search_literature_web, retrieve_literature_page
from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("gocam", instructions=SYSTEM)


from aurelian.dependencies.workdir import WorkDir

def deps() -> GOCAMDependencies:
    deps = GOCAMDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    
    # Get database connection parameters from environment if available
    db_path = os.getenv("GOCAM_DB_PATH")
    db_name = os.getenv("GOCAM_DB_NAME") 
    collection_name = os.getenv("GOCAM_COLLECTION_NAME")
    
    if db_path:
        deps.db_path = db_path
    if db_name:
        deps.db_name = db_name
    if collection_name:
        deps.collection_name = collection_name
        
    return deps

def ctx() -> RunContext[GOCAMDependencies]:
    rc: RunContext[GOCAMDependencies] = RunContext[GOCAMDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_gocams(query: str) -> List[Dict]:
    """
    Performs a retrieval search over the GO-CAM database.

    The query can be any text, such as name of a pathway, genes, or
    a complex sentence.

    The objects returned are summaries of GO-CAM models; they do not contain full
    details. Use `lookup_gocam` to retrieve full details of a model.

    This tool uses a retrieval method that is not guaranteed to always return
    complete results, and some results may be less relevant than others.
    You MAY use your judgment in filtering these.
    
    Args:
        query: The search query text
        
    Returns:
        List[Dict]: List of GOCAM models matching the query
    """
    return await gt.search_gocams(ctx(), query)


@mcp.tool()
async def lookup_gocam(model_id: str) -> Dict:
    """
    Performs a lookup of a GO-CAM model by its ID, and returns the model.
    
    Args:
        model_id: The ID of the GO-CAM model to look up
        
    Returns:
        Dict: The GO-CAM model data
    """
    return await gt.lookup_gocam(ctx(), model_id)


@mcp.tool()
async def lookup_uniprot_entry(uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number.

    This can be used to obtain further information about a protein in
    a GO-CAM.

    Args:
        uniprot_acc: The Uniprot accession
        
    Returns:
        str: Detailed functional and other info about the protein
    """
    return await gt.lookup_uniprot_entry(ctx(), uniprot_acc)


@mcp.tool()
async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed article by its PMID.

    Note that assertions in GO-CAMs may reference PMIDs, so this tool
    is useful for validating assertions. A common task is to align
    the text of a PMID with the text of an assertion, or extracting text
    snippets from the publication that support the assertion.
    
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


@mcp.tool()
async def inspect_file(data_file: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        data_file: name of file

    Returns:
        str: Contents of the file
    """
    return await fst.inspect_file(ctx(), data_file)


@mcp.tool()
async def list_files() -> str:
    """
    List files in the working directory.

    Returns:
        str: List of files in the working directory
    """
    return await fst.list_files(ctx())


@mcp.tool()
async def write_to_file(file_name: str, data: str) -> str:
    """
    Write data to a file in the working directory.

    Args:
        file_name: Name of the file to write
        data: Data to write to the file

    Returns:
        str: Confirmation message
    """
    return await fst.write_to_file(ctx(), file_name, data)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
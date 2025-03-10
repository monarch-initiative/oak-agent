"""
MCP tools for working with phenopacket databases.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.filesystem.filesystem_tools as fst
from aurelian.agents.phenopackets.phenopackets_agent import SYSTEM
import aurelian.agents.phenopackets.phenopackets_tools as pt
from aurelian.agents.phenopackets.phenopackets_config import PhenopacketsDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("phenopackets", instructions=SYSTEM)


from aurelian.dependencies.workdir import WorkDir

def deps() -> PhenopacketsDependencies:
    deps = PhenopacketsDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    
    # Get database connection parameters from environment if available
    db_path = os.getenv("PHENOPACKETS_DB_PATH")
    db_name = os.getenv("PHENOPACKETS_DB_NAME") 
    collection_name = os.getenv("PHENOPACKETS_COLLECTION_NAME")
    
    if db_path:
        deps.db_path = db_path
    if db_name:
        deps.db_name = db_name
    if collection_name:
        deps.collection_name = collection_name
        
    return deps

def ctx() -> RunContext[PhenopacketsDependencies]:
    rc: RunContext[PhenopacketsDependencies] = RunContext[PhenopacketsDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_phenopackets(query: str) -> List[Dict]:
    """
    Performs a retrieval search over the Phenopackets database.

    The query can be any text, such as name of a disease, phenotype, gene, etc.

    The objects returned are "Phenopackets" which is a structured representation
    of a patient. Each is uniquely identified by a phenopacket ID (essentially
    the patient ID).

    The objects returned are summaries of Phenopackets; some details such
    as phenotypes are omitted. Use `lookup_phenopacket` to retrieve full details.

    Args:
        query: The search query text

    Returns:
        List[Dict]: List of phenopackets matching the query
    """
    return await pt.search_phenopackets(ctx(), query)


@mcp.tool()
async def lookup_phenopacket(phenopacket_id: str) -> Dict:
    """
    Performs a lookup of an individual Phenopacket by its ID.

    IDs are typically of the form PMID_nnn_PatientNumber, but this should not be assumed.

    Args:
        phenopacket_id: The ID of the Phenopacket to look up

    Returns:
        Dict: The phenopacket data
    """
    return await pt.lookup_phenopacket(ctx(), phenopacket_id)


@mcp.tool()
async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed article by its PMID.
    
    A PMID should be of the form "PMID:nnnnnnn" (no underscores).
    
    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should not be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve and examine the `externalReferences` field.
    
    Args:
        pmid: The PubMed ID to look up
        
    Returns:
        str: Full text if available, otherwise abstract
    """
    return await pt.lookup_pmid(pmid)


@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web using a text query.
    
    Args:
        query: The search query
        
    Returns:
        str: Search results with summaries
    """
    return await pt.search_web(query)


@mcp.tool()
async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.
    
    Args:
        url: The URL to fetch
        
    Returns:
        str: The contents of the web page
    """
    return await pt.retrieve_web_page(url)


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
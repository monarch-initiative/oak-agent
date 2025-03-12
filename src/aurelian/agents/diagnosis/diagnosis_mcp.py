#!/usr/bin/env python
"""
MCP tools for performing diagnoses, validated against Monarch KG.
"""
import os

from mcp.server.fastmcp import FastMCP

import aurelian.agents.filesystem.filesystem_tools as fst
from aurelian.agents.diagnosis.diagnosis_agent import DIAGNOSIS_SYSTEM_PROMPT
from aurelian.agents.diagnosis.diagnosis_config import DiagnosisDependencies, get_config
from aurelian.agents.diagnosis.diagnosis_tools import (
    find_disease_id,
    find_disease_phenotypes,
)
from aurelian.utils.search_utils import web_search, retrieve_web_page as fetch_web_page
from aurelian.dependencies.workdir import WorkDir

# Initialize FastMCP server
mcp = FastMCP("diagnosis", instructions=DIAGNOSIS_SYSTEM_PROMPT)

def deps() -> DiagnosisDependencies:
    """Get diagnosis dependencies with workdir from environment."""
    deps = DiagnosisDependencies()
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/diagnosis")
    deps.workdir = WorkDir(loc)
    return deps

@mcp.tool()
async def search_disease(query: str) -> list:
    """
    Find diseases matching a search query.

    Args:
        query: The search term or expression to find diseases

    Returns:
        List of matching disease IDs and labels
    """
    return await find_disease_id(deps(), query)

@mcp.tool()
async def get_disease_phenotypes(disease_id: str) -> list:
    """
    Get phenotypes associated with a disease.

    Args:
        disease_id: The disease ID (e.g., "MONDO:0007947") or label

    Returns:
        List of phenotype associations for the disease
    """
    return await find_disease_phenotypes(deps(), disease_id)

@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note: This will not retrieve the full content. For that, use `retrieve_web_page`.

    Args:
        query: The search query

    Returns:
        Matching web pages plus summaries
    """
    return web_search(query)

@mcp.tool()
async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Args:
        url: The URL of the web page to retrieve

    Returns:
        The contents of the web page
    """
    return fetch_web_page(url)

@mcp.tool()
async def inspect_file(file_name: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        file_name: name of file to inspect

    Returns:
        File contents as string
    """
    return await fst.inspect_file(deps(), file_name)

@mcp.tool()
async def list_files() -> str:
    """
    List files in the working directory.

    Returns:
        Newline-separated list of file names
    """
    return "\n".join(deps().workdir.list_file_names())

@mcp.tool()
async def write_to_file(data: str, file_name: str) -> str:
    """
    Write data to a file in the working directory.

    Args:
        data: Content to write
        file_name: Target file name

    Returns:
        Confirmation message
    """
    print(f"Writing data to file: {file_name}")
    deps().workdir.write_file(file_name, data)
    return f"Data written to {file_name}"

@mcp.tool()
async def download_web_page(url: str, local_file_name: str) -> str:
    """
    Download contents of a web page to a local file.

    Args:
        url: URL of the web page
        local_file_name: Name of the local file to save to

    Returns:
        Confirmation message
    """
    print(f"Fetch URL: {url}")
    data = fetch_web_page(url)
    deps().workdir.write_file(local_file_name, data)
    return f"Data written to {local_file_name}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
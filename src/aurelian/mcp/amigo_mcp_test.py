"""
Test for AmiGO MCP functionality
"""
import os
import tempfile
from typing import List, Optional, Dict

# try to import, don't die if import fails
try:
    from mcp import Client
except ImportError:
    print("mcp package not found. Please install it to run this test.")
    Client = None

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


async def test_amigo_mcp():
    """Test the AmiGO MCP agent."""
    client = Client("/tmp/amigo-mcp", exec_args=["python", "-m", "aurelian.agents.amigo.amigo_mcp"])

    import time
    time.sleep(1)  # Give the server time to start

    # Set up a temporary working directory for the test
    tempdir = os.path.join(tempfile.gettempdir(), "test_amigo")
    os.makedirs(tempdir, exist_ok=True)
    os.environ["AURELIAN_WORKDIR"] = tempdir

    # For testing - would normally come from configuration
    os.environ["AMIGO_TAXON"] = "9606"  # Human

    convo: List[Message] = []

    def add_to_convo(role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        convo.append(msg)
        return msg

    # Make a query
    add_to_convo("user", "What tools are available for working with Gene Ontology?")

    message = convo[-1].content

    response = await client.chat(messages=message)
    print(f"Got response: {response}")

    # Get available tools
    tool_choices = await client.get_tool_choice(messages=convo)
    print(f"Available tools: {[t['id'] for t in tool_choices]}")

    # Test gene association lookup
    find_gene_associations_tool = next((t for t in tool_choices if t["id"] == "find_gene_associations"), None)
    if find_gene_associations_tool:
        print(f"Testing find_gene_associations tool...")
        tool_input = '{"gene_id": "UniProtKB:P04637"}'  # p53
        try:
            tool_result = await client.execute_tool(tool_id=find_gene_associations_tool["id"], tool_input=tool_input)
            print(f"find_gene_associations result length: {len(tool_result)}")
            print(f"First result: {tool_result[:200]}...")  # Just show first 200 chars
        except Exception as e:
            print(f"find_gene_associations failed (expected in test): {e}")

    # Test PMID lookup
    lookup_pmid_tool = next((t for t in tool_choices if t["id"] == "lookup_pmid"), None)
    if lookup_pmid_tool:
        print(f"Testing lookup_pmid tool...")
        tool_input = '{"pmid": "PMID:19661248"}'
        try:
            tool_result = await client.execute_tool(tool_id=lookup_pmid_tool["id"], tool_input=tool_input)
            print(f"lookup_pmid result length: {len(tool_result)}")
            print(f"First part of result: {tool_result[:200]}...")
        except Exception as e:
            print(f"lookup_pmid failed (expected in test): {e}")

    await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_amigo_mcp())

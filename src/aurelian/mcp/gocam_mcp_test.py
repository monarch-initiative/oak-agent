"""
Test for GOCAM MCP functionality
"""
import os
import tempfile
from typing import List, Optional, Dict

from mcp import Client
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


async def test_gocam_mcp():
    """Test the GOCAM MCP agent."""
    client = Client("/tmp/gocam-mcp", exec_args=["python", "-m", "aurelian.agents.gocam.gocam_mcp"])

    import time
    time.sleep(1)  # Give the server time to start

    # Set up a temporary working directory for the test
    tempdir = os.path.join(tempfile.gettempdir(), "test_gocam")
    os.makedirs(tempdir, exist_ok=True)
    os.environ["AURELIAN_WORKDIR"] = tempdir

    # For testing without a real database - would normally come from configuration
    os.environ["GOCAM_DB_PATH"] = "mongodb://localhost:27017/test_gocams"
    os.environ["GOCAM_DB_NAME"] = "test_gocams"
    os.environ["GOCAM_COLLECTION_NAME"] = "test_main"

    convo: List[Message] = []

    def add_to_convo(role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        convo.append(msg)
        return msg

    # Make a query
    add_to_convo("user", "What tools are available for working with GO-CAMs?")

    message = convo[-1].content

    response = await client.chat(messages=message)
    print(f"Got response: {response}")

    # Get available tools
    tool_choices = await client.get_tool_choice(messages=convo)
    print(f"Available tools: {[t['id'] for t in tool_choices]}")

    # Test the list_files tool
    list_files_tool = next((t for t in tool_choices if t["id"] == "list_files"), None)
    if list_files_tool:
        print(f"Testing list_files tool...")
        tool_input_schema = await client.get_tool_input_schema(tool_id=list_files_tool["id"])
        tool_result = await client.execute_tool(tool_id=list_files_tool["id"], tool_input='{}')
        print(f"list_files result: {tool_result}")
    
    # Create a test file
    write_file_tool = next((t for t in tool_choices if t["id"] == "write_to_file"), None)
    if write_file_tool:
        print(f"Testing write_to_file tool...")
        tool_input = '{"file_name": "gocam_test.txt", "data": "This is a test file for GOCAM MCP"}'
        tool_result = await client.execute_tool(tool_id=write_file_tool["id"], tool_input=tool_input)
        print(f"write_to_file result: {tool_result}")
    
    # Check if the file was created
    if list_files_tool:
        tool_result = await client.execute_tool(tool_id=list_files_tool["id"], tool_input='{}')
        print(f"list_files after writing: {tool_result}")
    
    # Read the file
    inspect_file_tool = next((t for t in tool_choices if t["id"] == "inspect_file"), None)
    if inspect_file_tool:
        print(f"Testing inspect_file tool...")
        tool_input = '{"data_file": "gocam_test.txt"}'
        tool_result = await client.execute_tool(tool_id=inspect_file_tool["id"], tool_input=tool_input)
        print(f"inspect_file result: {tool_result}")
    
    # Try search function
    search_tool = next((t for t in tool_choices if t["id"] == "search_gocams"), None)
    if search_tool:
        print(f"Testing search_gocams tool...")
        tool_input = '{"query": "apoptosis"}'
        try:
            tool_result = await client.execute_tool(tool_id=search_tool["id"], tool_input=tool_input)
            print(f"search_gocams result: {tool_result[:200]}...")  # Just show first 200 chars
        except Exception as e:
            print(f"search_gocams failed (expected in test): {e}")
    
    await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gocam_mcp())
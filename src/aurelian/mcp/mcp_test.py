"""
MCP tools for creating LinkML schemas and example datasets
"""
import sys

from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("test")

@mcp.tool()
async def add_two_numbers(n1: int, n2: int) -> int:
    """
    Add two numbers together.

    Args:
        n1: first number
        n2: second number

    Returns:
        sum of the two numbers
    """
    return n1 + n2


if __name__ == "__main__":
    print("Running the LinkML MCP tools")
    print("Use Ctrl-C to exit", file=sys.stderr)
    # Initialize and run the server
    mcp.run(transport='stdio')
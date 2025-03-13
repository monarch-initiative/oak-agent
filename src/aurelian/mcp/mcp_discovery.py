#!/usr/bin/env python
"""
Script for discovering and testing MCP implementations.
"""

import argparse
import importlib
import inspect
import sys
from pathlib import Path
from typing import List, Optional


def list_mcp_tools(module_path: str) -> List[str]:
    """
    List all MCP tools in a given module.
    
    Args:
        module_path: Dot-separated path to the module
        
    Returns:
        List of tool names
    """
    try:
        # Import the module
        module = importlib.import_module(module_path)
        
        # Find the MCP server instance
        mcp = getattr(module, "mcp", None)
        if not mcp:
            print(f"No 'mcp' instance found in {module_path}")
            return []
        
        # Get all functions with the MCP tool decorator
        tools = []
        for name, func in inspect.getmembers(module, inspect.isfunction):
            # Check if this function is an MCP tool
            if hasattr(func, "__mcp_tool__") and func.__mcp_tool__ is True:
                tools.append(name)
                
        return tools
    except Exception as e:
        print(f"Error importing {module_path}: {e}")
        return []


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Discover and test MCP implementations")
    parser.add_argument("--agent", "-a", help="Agent type to test (e.g., 'diagnosis')")
    parser.add_argument("--list", "-l", action="store_true", help="List available MCP modules")
    args = parser.parse_args()
    
    # Base path for agent modules
    base_path = Path(__file__).parent.parent
    
    if args.list:
        # List all MCP modules
        agents_dir = base_path / "agents"
        print("Available MCP modules:")
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                mcp_file = agent_dir / f"{agent_dir.name}_mcp.py"
                if mcp_file.exists():
                    print(f"  - {agent_dir.name}")
        return
        
    if not args.agent:
        print("Error: Please specify an agent type with --agent")
        sys.exit(1)
        
    # Check if the MCP module exists
    agent_type = args.agent
    module_path = f"aurelian.agents.{agent_type}.{agent_type}_mcp"
    
    # List the tools
    tools = list_mcp_tools(module_path)
    if tools:
        print(f"MCP tools for {agent_type}:")
        for tool in tools:
            print(f"  - {tool}")
    else:
        print(f"No MCP tools found for {agent_type}")


if __name__ == "__main__":
    main()
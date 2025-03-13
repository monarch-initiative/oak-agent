#!/usr/bin/env python
"""
MCP Configuration Generator

Utility script to generate Model Context Protocol (MCP) server configuration from a simplified input.
"""

import json
import os
import argparse
from typing import Dict, Optional, Any
from pathlib import Path


class MCPConfigGenerator:
    """Generator for MCP server configuration."""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the MCP config generator.

        Args:
            base_dir: Base directory for resolving relative paths (defaults to current working directory)
        """
        self.base_dir = base_dir or os.getcwd()

    def generate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a full MCP server configuration from a simplified config.

        Args:
            config: Simplified configuration dictionary

        Returns:
            Complete MCP server configuration
        """
        mcp_servers = {}

        for server_name, server_config in config.items():
            server_type = server_config.get("type", "custom")

            if server_type == "memory":
                # Memory server configuration
                memory_path = server_config.get("memory_path", os.path.expanduser("~/.mcp/memory.json"))
                mcp_servers[server_name] = {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "env": {"MEMORY_FILE_PATH": memory_path},
                }
            elif server_type in ["linkml", "gocam", "phenopackets", "robot", "amigo", "uniprot", "diagnosis"]:
                # Aurelian agent MCP server
                agent_script = f"src/aurelian/agents/{server_type}/{server_type}_mcp.py"
                workdir = server_config.get("workdir", f"/tmp/{server_type}")

                # Construct environment variables
                env = {"AURELIAN_WORKDIR": workdir}

                # Add optional environment variables
                if "email" in server_config:
                    env["EMAIL"] = server_config["email"]
                if "doi_urls" in server_config:
                    env["DOI_FULL_TEXT_URLS"] = server_config["doi_urls"]

                # Add any additional env vars from config
                if "env" in server_config:
                    env.update(server_config["env"])

                script_path = str(Path(self.base_dir) / agent_script)
                mcp_servers[server_name] = {
                    "command": server_config.get("python_path", "/usr/bin/python"),
                    "args": [script_path],
                    "env": env,
                }
            elif server_type == "custom":
                # Custom server configuration (direct passthrough)
                mcp_servers[server_name] = {
                    "command": server_config["command"],
                    "args": server_config["args"],
                    "env": server_config.get("env", {}),
                }

        return {"mcpServers": mcp_servers}

    def write_config(self, config: Dict[str, Any], output_path: str) -> None:
        """
        Write the generated configuration to a file.

        Args:
            config: The simplified configuration dictionary
            output_path: Path to write the generated configuration
        """
        full_config = self.generate_config(config)

        with open(output_path, "w") as f:
            json.dump(full_config, f, indent=2)

        print(f"MCP configuration written to {output_path}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate MCP server configuration")
    parser.add_argument("--config", "-c", required=True, help="Path to simplified config file")
    parser.add_argument("--output", "-o", required=True, help="Path to write generated config")
    parser.add_argument("--base-dir", "-b", help="Base directory for resolving paths")
    return parser.parse_args()


def main():
    """Main entrypoint."""
    args = parse_args()

    # Load simplified config
    with open(args.config) as f:
        config = json.load(f)

    # Generate and write config
    generator = MCPConfigGenerator(base_dir=args.base_dir)
    generator.write_config(config, args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Example script to generate a sample MCP configuration file using the config generator.
"""

import os
import json
from pathlib import Path
from config_generator import MCPConfigGenerator

# Define the base directory for Aurelian
aurelian_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
print(f"Aurelian directory: {aurelian_dir}")

# Create a simple configuration
simple_config = {
    "memory": {"type": "memory", "memory_path": "~/.mcp/memory.json"},
    "linkml": {"type": "linkml", "workdir": "/tmp/linkml"},
    "gocam": {
        "type": "gocam",
        "workdir": "/tmp/gocam",
        "email": "user@example.com",
        "doi_urls": "https://example.com/doi-resolver",
    },
}

# Generate the configuration
generator = MCPConfigGenerator(base_dir=str(aurelian_dir))
full_config = generator.generate_config(simple_config)

# Write to a file
output_path = aurelian_dir / "mcp-config.json"
with open(output_path, "w") as f:
    json.dump(full_config, f, indent=2)

print(f"Generated MCP configuration at: {output_path}")
print("Use with: mcp start --config mcp-config.json")

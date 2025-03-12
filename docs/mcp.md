# Model Context Protocol (MCP) Integration

This document describes how to set up and use [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) with Aurelian agents.

## What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes how applications provide context to LLMs. It works like a "USB-C port for AI applications," providing a standardized way to connect AI models to different data sources and tools.

### Key benefits:

- Connect LLMs to pre-built integrations with a standard protocol
- Flexibility to switch between LLM providers
- Secure your data within your infrastructure
- Enable complex agent workflows

## Setting Up MCP Servers for Aurelian

Aurelian provides MCP server implementations for several of its agents. You can use these servers to expose Aurelian's capabilities to any MCP-compatible client (such as Claude).

### Configuration Options

You can configure MCP servers in two ways:

1. **Manual Configuration**: Create the full JSON configuration directly
2. **Generated Configuration**: Use the provided config generator script

### Option 1: Manual Configuration

Create a file named `mcp-config.json` with your server configurations:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {
        "MEMORY_FILE_PATH": "~/.mcp/memory.json"
      }
    },
    "linkml": {
      "command": "python",
      "args": [
        "/path/to/aurelian/src/aurelian/agents/linkml/linkml_mcp.py"
      ],
      "env": {
        "AURELIAN_WORKDIR": "/tmp/linkml"
      }
    }
  }
}
```

### Option 2: Generated Configuration

1. Create a simplified configuration file (e.g., `simple-config.json`):

```json
{
  "memory": {
    "type": "memory",
    "memory_path": "~/.mcp/memory.json"
  },
  "linkml": {
    "type": "linkml",
    "workdir": "/tmp/linkml",
    "python_path": "/usr/bin/python"
  }
}
```

2. Generate the full configuration:

```bash
python src/aurelian/mcp/config_generator.py --config simple-config.json --output mcp-config.json --base-dir /path/to/aurelian
```

### Available Agent Servers

Aurelian provides the following MCP servers:

| Server Name   | Type          | Description                                        |
|---------------|---------------|----------------------------------------------------|
| linkml        | Agent         | LinkML schema validation and data modeling         |
| gocam         | Agent         | Gene Ontology Causal Activity Models               |
| phenopackets  | Agent         | Working with phenotype data in Phenopacket format  |
| robot         | Agent         | Ontology manipulation with ROBOT                   |
| amigo         | Agent         | Gene Ontology and gene associations                |
| uniprot       | Agent         | UniProt protein information                        |
| diagnosis     | Agent         | Disease diagnosis with Monarch Knowledge Graph     |
| memory        | Utility       | Persistent memory for MCP interactions             |

### Configuration Parameters

#### Common Parameters for Agent Servers

- `type`: The agent type (e.g., "linkml", "gocam")
- `workdir`: Directory for the agent to store files (default: `/tmp/{agent_type}`)
- `python_path`: Path to Python executable (default: `/usr/bin/python`)
- `email`: Email address for services that require it (optional)
- `doi_urls`: DOI URL pattern for literature-related agents (optional)
- `env`: Additional environment variables (optional)

#### Memory Server Parameters

- `type`: Always "memory"
- `memory_path`: Path to store memory file (default: `~/.mcp/memory.json`)

#### Custom Server Parameters

- `type`: "custom"
- `command`: Executable command
- `args`: List of command arguments
- `env`: Environment variables dictionary

## Running MCP with Claude

1. Install the MCP CLI:

```bash
npm install -g @modelcontextprotocol/cli
```

2. Start the MCP servers:

```bash
mcp start --config mcp-config.json
```

3. Open Claude and ensure MCP is enabled in settings

4. In Claude, you can now interact with your Aurelian agents through MCP

## Example Use Cases

- **LinkML Validation**: Use Claude to validate data against LinkML schemas
- **Ontology Management**: Create and manipulate ontologies through natural language
- **Gene Association Analysis**: Ask questions about gene functions and associations
- **Phenotype Analysis**: Work with structured phenotype data

## Troubleshooting

- Ensure the correct Python environment is activated for each server
- Check server logs for errors by running `mcp logs`
- Verify paths in your configuration are correct and accessible
- Ensure required environment variables are set properly
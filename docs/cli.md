# Command Line Interface

Aurelian provides a powerful command-line interface (CLI) for accessing its various agents and utilities. The CLI follows a consistent pattern that allows running agents in either direct query mode or interactive UI mode.

## Usage Patterns

### UI Mode

To start an agent in UI mode (interactive chat interface):

```bash
aurelian <agent-name> --ui
```

Example:
```bash
aurelian diagnosis --ui
```

This starts the Diagnosis agent with a chat interface where you can interactively ask questions.

### Direct Query Mode

To run an agent with a direct query and get the response immediately:

```bash
aurelian <agent-name> "your query here"
```

Example:
```bash
aurelian diagnosis "Patient with hypotonia, seizures, and developmental delay"
```

This processes the query directly and prints the result to the console.

## Common Options

All agent commands support these common options:

- `--model`, `-m`: Specify the model to use for the agent
- `--workdir`, `-w`: Set the working directory (default: "workdir")
- `--share/--no-share`: Share the agent UI via public URL (default: no-share)
- `--server-port`, `-p`: Set the server port for UI mode (default: 7860)
- `--ui/--no-ui`: Force UI mode even with a query (default: no-ui)

## Available Agents

Aurelian provides specialized agents for various scientific and biomedical tasks. Each agent can be accessed via its dedicated subcommand:

| Command | Description |
|---------|-------------|
| `amigo` | Gene Ontology and gene product annotations |
| `biblio` | Bibliographic data and citations management |
| `checklist` | Paper evaluation against established checklists |
| `chemistry` | Chemical structure analysis |
| `datasheets` | Extract dataset metadata according to Datasheets for Datasets schema |
| `diagnosis` | Rare disease diagnosis using the Monarch Knowledge Base |
| `gocam` | Gene Ontology Causal Activity Models |
| `linkml` | Data modeling and schema validation |
| `literature` | Scientific publication analysis |
| `mapper` | Ontology mapping and term translation |
| `monarch` | Biomedical knowledge graph exploration |
| `phenopackets` | Standardized phenotype data in GA4GH format |
| `rag` | Retrieval-augmented generation for document collections |
| `robot` | Ontology operations and manipulations |
| `ubergraph` | SPARQL-based ontology queries |

## Utility Commands

The CLI also provides several utility commands:

| Command | Description |
|---------|-------------|
| `fulltext <pmid>` | Download full text for a PubMed article |
| `websearch <term>` | Search the web for a query term |
| `geturl <url>` | Retrieve content from a URL |
| `search-ontology <ontology> <term>` | Search an ontology for a term |

## Full Command Reference

::: mkdocs-click
    :module: aurelian.cli
    :command: main
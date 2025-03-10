# UniProt Agent

::: aurelian.agents.uniprot.uniprot_agent

The UniProt agent provides an interface to the UniProt database, allowing you to search for proteins, retrieve detailed information about specific proteins, and map between different database identifiers.

## Features

- Search UniProt for protein information using keywords, gene names, or other attributes
- Retrieve detailed information about specific proteins using UniProt accession numbers
- Map UniProt accessions to entries in other databases (like PDB, KEGG, etc.)
- Handle normalized UniProt IDs (with or without version numbers or database prefixes)

## Examples

### Searching UniProt

```
Find all human insulin proteins
```

### Looking up a specific protein

```
Get detailed information for UniProt accession P01308
```

### Mapping identifiers

```
Map the UniProt IDs P01308 and P01009 to PDB database
```

## Technical Details

The UniProt agent uses the [bioservices](https://bioservices.readthedocs.io/en/master/) Python package to interact with the UniProt API. It formats and processes the results for easier interpretation.

### Tools

- `search`: Searches UniProt with a query string and returns results in TSV format
- `lookup_uniprot_entry`: Retrieves detailed information for a specific UniProt accession number
- `uniprot_mapping`: Maps UniProt accessions to entries in other databases

## Configuration

The UniProt agent can be configured using environment variables:

- `AURELIAN_WORKDIR`: Directory for storing temporary files and results (optional)

## Using the Agent

### Python API

```python
from aurelian.agents.uniprot import uniprot_agent

# Run the agent with a query
result = uniprot_agent.run_sync("Find information about human insulin")
print(result)

# Use specific tools directly
from aurelian.agents.uniprot import lookup_uniprot_entry
from pydantic_ai import RunContext

ctx = RunContext()
result = lookup_uniprot_entry(ctx, "P01308")
print(result)
```

### Command Line

```bash
python -m aurelian.cli run uniprot "Find information about human insulin"
```

### Web Interface

```bash
python -m aurelian.cli serve uniprot
```
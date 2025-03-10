# Monarch Agent

The Monarch agent provides an interface to the Monarch Knowledge Base, allowing you to search for and explore relationships between genes, diseases, phenotypes, and other biomedical entities.

## Features

- Find associations for genes, including what diseases they're linked to
- Find associations for diseases, including what genes and phenotypes they're linked to
- Provide information about biological relationships in a structured way
- Normalize biomedical identifiers for consistent querying

## Examples

### Finding Gene Associations

```
Find all diseases associated with the BRCA1 gene
```

### Finding Disease Associations

```
What genes are associated with Alzheimer's disease?
```

### Exploring Phenotypes

```
Find phenotypes associated with MONDO:0007254
```

## Technical Details

The Monarch agent uses the OakLib library to interact with the Monarch Knowledge Base. It provides tools to search and query the rich biomedical relationships in this database.

### Tools

- `find_gene_associations`: Retrieves associations for a given gene ID
- `find_disease_associations`: Retrieves associations for a given disease ID

## Configuration

The Monarch agent can be configured using environment variables:

- `AURELIAN_WORKDIR`: Directory for storing temporary files and results (optional)
- `MONARCH_TAXON`: Default taxonomic ID to use (defaults to 9606 for human)

## Using the Agent

### Python API

```python
from aurelian.agents.monarch import monarch_agent

# Run the agent with a query
result = monarch_agent.run_sync("Find associations for gene BRCA1")
print(result)

# Use specific tools directly
from aurelian.agents.monarch import find_gene_associations
from pydantic_ai import RunContext

ctx = RunContext()
result = find_gene_associations(ctx, "BRCA1")
print(result)
```

### Command Line

```bash
python -m aurelian.cli run monarch "Find diseases associated with BRCA1 gene"
```

### Web Interface

```bash
python -m aurelian.cli serve monarch
```
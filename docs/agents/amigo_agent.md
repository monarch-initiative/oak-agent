# AmiGO Agent

::: aurelian.agents.amigo.amigo_agent

The AmiGO Agent provides a natural language interface to the Gene Ontology (GO) through the AmiGO service. It helps users search for GO terms, retrieve information about genes and their functions, and explore relationships between biological processes, molecular functions, and cellular components.

## Features

- Search for GO terms using natural language queries
- Retrieve detailed information about specific genes
- Explore GO annotations for genes of interest
- Find relationships between biological processes, molecular functions, and cellular components
- Access GO term definitions and hierarchies

## Usage

### Python API

```python
from aurelian.agents.amigo import amigo_agent, get_config

# Initialize dependencies
deps = get_config()

# Query information about a gene
result = await amigo_agent.run(
    "Tell me about the function of the TP53 gene",
    deps=deps
)

# Get the response
print(result.data)
```

### Command Line Interface

```bash
aurelian amigo "Tell me about the function of the TP53 gene"
```

### Gradio Interface

```python
from aurelian.agents.amigo import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The AmiGO Agent provides the following tools:

### search_go_terms

Searches the Gene Ontology for terms matching a query string.

### search_genes

Searches for genes by name, symbol, or description.

### get_go_term_info

Retrieves detailed information about a specific GO term.

### get_gene_info

Retrieves detailed information about a specific gene.

## Examples

### Example 1: Searching for a GO term

```
What GO terms are related to apoptosis?
```

### Example 2: Getting information about a gene

```
Tell me about the function of the TP53 gene
```

### Example 3: Exploring relationships between GO terms

```
What is the relationship between DNA repair and cell cycle?
```
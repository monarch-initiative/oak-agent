# GO-CAM Agent

::: aurelian.agents.gocam.gocam_agent

The GO-CAM Agent assists with creating, editing, and understanding Gene Ontology Causal Activity Models (GO-CAMs). It provides tools for working with GO terms, genes, and modeling biological pathways using the GO-CAM framework.

## Features

- Search for GO terms and gene products
- Create and edit GO-CAM models
- Explain GO-CAM concepts and best practices
- Visualize biological processes and molecular functions
- Convert between different GO-CAM representations

## Usage

### Python API

```python
from aurelian.agents.gocam import gocam_agent, get_config

# Initialize dependencies
deps = get_config()

# Query about GO-CAM
result = await gocam_agent.run(
    "How do I represent a phosphorylation process in GO-CAM?",
    deps=deps
)

# Get the response
print(result.data)
```

### Command Line Interface

```bash
aurelian gocam "How do I represent a phosphorylation process in GO-CAM?"
```

### Gradio Interface

```python
from aurelian.agents.gocam import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The GO-CAM Agent provides the following tools:

### search_go_terms

Searches the Gene Ontology for terms matching a query string.

### search_genes

Searches for genes by name, symbol, or description.

### create_gocam_model

Creates a new GO-CAM model with specified components.

### visualize_gocam

Generates a visualization of a GO-CAM model.

## Examples

### Example 1: Creating a simple GO-CAM model

```
Create a GO-CAM model for TP53 regulating apoptosis
```

### Example 2: Finding relevant GO terms

```
What GO terms are related to DNA repair?
```

### Example 3: Explaining GO-CAM concepts

```
Explain how to represent a protein kinase activity in GO-CAM
```

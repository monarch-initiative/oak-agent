# Ontology Mapper Agent

The Ontology Mapper agent helps users find and map terms in OBO ontologies based on natural language queries, alternative names, or descriptions. It uses semantic search capabilities to locate the most relevant ontology terms.

## Features

- Search across multiple OBO ontologies for relevant terms
- Map natural language descriptions to standard ontology terms
- Evaluate relevance of potential matches based on context
- Provide guidance when no exact matches exist
- Link to external resources for additional information

## Examples

### Finding terms in specific ontologies

```
Find the term in the cell ontology for neuron
```

```
What is the term for the process of cell division in GO?
```

### Mapping multiple terms

```
Find good MP terms for the following:

* Surface righting Reduced
* Contextual fear conditioning Reduced
* Morris water maze Reduced
* Rotarod Increased
```

### Finding anatomical terms

```
Best terms to use for the middle 3 fingers
```

## Technical Details

The Ontology Mapper agent uses embedding-based search to find terms that are semantically similar to the query. It works with a configurable set of ontologies from the OBO Foundry.

### Tools

- `search_terms`: Finds similar ontology terms to the search query
- `search_web`: Searches the web for additional information
- `retrieve_web_page`: Fetches the contents of a web page for additional context

### Supported Ontologies

By default, the agent supports the following ontologies:
- MONDO: Disease ontology
- HP: Human Phenotype Ontology
- GO: Gene Ontology
- UBERON: Anatomy ontology
- CL: Cell Ontology
- MP: Mammalian Phenotype Ontology
- ENVO: Environment Ontology

Additional ontologies can be specified when starting the agent.

## Configuration

The Ontology Mapper agent can be configured using environment variables:

- `MAX_SEARCH_RESULTS`: Maximum number of search results to return (default: 30)
- `AURELIAN_WORKDIR`: Directory for storing temporary files and results (optional)

## Using the Agent

### Python API

```python
from aurelian.agents.ontology_mapper import ontology_mapper_agent, get_config

# Configure with specific ontologies
config = get_config(ontologies=["cl", "uberon", "go"])

# Run the agent with a query
result = ontology_mapper_agent.run_sync("Find terms for neurons in the hippocampus", deps=config)
print(result)
```

### Command Line

```bash
# Run with default ontologies
python -m aurelian.cli mapper "Find the term in the cell ontology for neuron"

# Run with specific ontologies
python -m aurelian.cli mapper --ontologies cl,uberon,go "Find terms for neurons in the hippocampus"
```

### Web Interface

```bash
# Start with default ontologies
python -m aurelian.cli mapper

# Start with specific ontologies
python -m aurelian.cli mapper --ontologies cl,uberon,go
```
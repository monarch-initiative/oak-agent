# UberGraph Agent

::: aurelian.agents.ubergraph.ubergraph_agent

The UberGraph agent provides a natural language interface to query ontologies using SPARQL through the UberGraph endpoint. It helps users formulate and execute SPARQL queries without needing to know the full SPARQL syntax.

## Features

- Convert natural language questions into SPARQL queries
- Query the UberGraph SPARQL endpoint, which contains many OBO ontologies
- Access precomputed relation graph edges 
- Use a comprehensive set of predefined SPARQL prefixes
- Get results in a simplified, readable format

## Examples

### Finding Anatomical Structures

```
Find all cell types that are part of the heart
```

### Retrieving Definitions

```
What is the definition of CL:0000746?
```

### Gene Expression

```
What genes are expressed in neurons?
```

### Class Hierarchy

```
What are the subclasses of skeletal muscle tissue?
```

## Technical Details

The UberGraph agent connects to the UberGraph SPARQL endpoint, which is a triplestore containing many OBO ontologies and precomputed relation graph edges.

### Tools

- `query_ubergraph`: Performs a SPARQL query over UberGraph and returns the results

### UberGraph Data Model Assumptions

The agent operates with these assumptions about the UberGraph data model:

- Direct (asserted) edges are stored in the `renci:ontology` graph
- Indirect (entailed) edges are stored in the `renci:redundant` graph
- rdfs:subClassOf is used for is-a relationships
- rdfs:label is used for labels
- IAO:0000115 is used for definitions
- oboInOwl:hasExactSynonym is used for synonyms
- oboInOwl:hasDbXref is used for cross-references

## Configuration

The UberGraph agent can be configured using environment variables:

- `UBERGRAPH_ENDPOINT`: The URL of the UberGraph SPARQL endpoint
- `MAX_RESULTS`: Maximum number of results to return (default: 20)
- `AURELIAN_WORKDIR`: Directory for storing temporary files and results (optional)

## Using the Agent

### Python API

```python
from aurelian.agents.ubergraph import ubergraph_agent, get_config

# Configure with specific endpoint
config = get_config(endpoint="https://ubergraph.apps.renci.org/sparql")

# Run the agent with a query
result = ubergraph_agent.run_sync("What are the subclasses of neuron?", deps=config)
print(result)
```

### Command Line

```bash
# Direct query
python -m aurelian.cli ubergraph "Find all cell types that are part of the heart"

# Start chat interface
python -m aurelian.cli ubergraph
```

### Web Interface

```bash
python -m aurelian.cli ubergraph
```
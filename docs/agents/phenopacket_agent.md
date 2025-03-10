# Phenopacket Agent

The Phenopacket Agent provides a natural language interface for working with GA4GH Phenopackets, a standard format for sharing disease and phenotype information for genomic medicine. It helps users create, analyze, and interpret phenopackets for rare disease diagnosis and research.

## Features

- Create and validate phenopackets from natural language descriptions
- Search and analyze phenopacket databases
- Extract phenotypes, diseases, and genetic variants from clinical descriptions
- Convert between phenopacket formats
- Assist with rare disease diagnosis
- Generate human-readable summaries of phenopackets

## Usage

### Python API

```python
from aurelian.agents.phenopackets import phenopackets_agent, get_config

# Initialize dependencies
deps = get_config()

# Query phenopacket information
result = await phenopackets_agent.run(
    "Create a phenopacket for a patient with Marfan syndrome",
    deps=deps
)

# Get the response
print(result.data)
```

### Command Line Interface

```bash
aurelian phenopackets "Create a phenopacket for a patient with Marfan syndrome"
```

### Gradio Interface

```python
from aurelian.agents.phenopackets import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The Phenopacket Agent provides the following tools:

### create_phenopacket

Creates a new phenopacket from a description of phenotypes, diseases, and variants.

### validate_phenopacket

Validates a phenopacket against the schema.

### search_phenopackets

Searches a phenopacket database for matching cases.

### summarize_phenopacket

Generates a human-readable summary of a phenopacket.

## Examples

### Example 1: Creating a phenopacket

```
Create a phenopacket for a 5-year-old male with osteogenesis imperfecta
```

### Example 2: Searching for similar cases

```
Find phenopackets with similar phenotypes to: HP:0000347, HP:0001382, HP:0011304
```

### Example 3: Analyzing a phenopacket

```
Summarize the clinical information in this phenopacket:
```
```json
{
  "id": "example-patient",
  "subject": {
    "id": "patient1",
    "timeAtLastEncounter": {
      "age": {
        "iso8601duration": "P5Y"
      }
    },
    "sex": "MALE"
  },
  "phenotypicFeatures": [
    {
      "type": {
        "id": "HP:0000347",
        "label": "Micrognathia"
      }
    },
    {
      "type": {
        "id": "HP:0001382",
        "label": "Joint hypermobility"
      }
    }
  ]
}
```
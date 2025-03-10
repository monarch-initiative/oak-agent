# Diagnosis Agent

The Diagnosis agent assists in diagnosing rare diseases by leveraging the Monarch Knowledge Base. It helps clinical geneticists evaluate potential conditions based on patient phenotypes and validates diagnostic hypotheses against known disease-phenotype associations.

## Features

- Identify candidate diseases based on phenotype descriptions
- Find disease IDs in the MONDO ontology
- Retrieve phenotypes associated with specific diseases
- Compare patient phenotypes with known disease manifestations
- Provide detailed reasoning and evidence for diagnoses
- Search medical literature for additional context

## Examples

### Disease Diagnosis

```
Patient has growth failure, distinct facial features, alopecia, and skin aging.
Findings excluded: Pigmented nevi, cafe-au-lait spots, and photosensitivity.
Onset was in infancy.
Return diagnosis with MONDO ID
```

### Specific Disease Phenotypes

```
What eye phenotypes does Marfan syndrome have?
```

### Disease Classification

```
What are the kinds of Ehlers-Danlos syndrome?
```

### Knowledge Base Validation

```
Look at phenotypes for Ehlers-Danlos classic type 2. 
Do a literature search to look at latest studies. 
What is missing from the KB?
```

## Technical Details

The Diagnosis agent uses the Monarch Knowledge Base and MONDO ontology to find and validate disease-phenotype associations.

### Tools

- `find_disease_id`: Finds disease IDs in the MONDO ontology based on search terms
- `find_disease_phenotypes`: Retrieves phenotypes associated with a specific disease ID
- `search_web`: Searches the web for additional information
- `retrieve_web_page`: Fetches the contents of a web page for detailed analysis

## Configuration

The Diagnosis agent can be configured using environment variables:

- `MAX_SEARCH_RESULTS`: Maximum number of search results to return (default: 10)
- `AURELIAN_WORKDIR`: Directory for storing temporary files and results (optional)

## Using the Agent

### Python API

```python
from aurelian.agents.diagnosis import diagnosis_agent, get_config

# Configure with specific settings
config = get_config()
config.max_search_results = 20

# Run the agent with a query
result = diagnosis_agent.run_sync(
    "Patient has growth failure, distinct facial features, alopecia, and skin aging.",
    deps=config
)
print(result)
```

### Command Line

```bash
# Direct query
python -m aurelian.cli diagnosis "What eye phenotypes does Marfan syndrome have?"

# Start chat interface
python -m aurelian.cli diagnosis
```

### Web Interface

```bash
python -m aurelian.cli diagnosis
```
# Checklist Agent

The Checklist Agent evaluates scientific papers against established checklists such as STREAMS, STORMS, and ARRIVE. It helps ensure that papers conform to relevant reporting guidelines and best practices.

## Features

- Automatic selection of appropriate checklists based on paper content
- Detailed evaluation of papers against each checklist item
- Support for PubMed IDs and DOIs for paper retrieval
- Provides PASS/FAIL/OTHER evaluations with explanations for each checklist item
- Returns results as a structured markdown table

## Usage

### Python API

```python
from aurelian.agents.checklist import checklist_agent, get_config

# Initialize dependencies
deps = get_config()

# Evaluate a paper against a specific checklist
result = await checklist_agent.run(
    "Evaluate https://journals.asm.org/doi/10.1128/mra.01361-19 using STREAMS",
    deps=deps
)

# Get the evaluation results
print(result.data)
```

### Command Line Interface

```bash
aurelian checklist "Evaluate https://journals.asm.org/doi/10.1128/mra.01361-19 using STREAMS"
```

### Gradio Interface

```python
from aurelian.agents.checklist import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The Checklist Agent provides the following tools:

### retrieve_text_from_pmid

Retrieves the full text or abstract of a paper using its PubMed ID.

### retrieve_text_from_doi

Retrieves the full text or abstract of a paper using its DOI.

### fetch_checklist

Retrieves a specific checklist by ID (e.g., STREAMS, STORMS, ARRIVE).

## Available Checklists

The agent supports various checklists for different types of scientific papers:

- **STREAMS**: Standards for Reporting Engineered Mammalian Systems
- **STORMS**: STrengthening the Reporting Of Molecular Simulations
- **ARRIVE**: Animal Research: Reporting of In Vivo Experiments

## Examples

### Example 1: Evaluating a paper using STREAMS

```
Evaluate https://journals.asm.org/doi/10.1128/mra.01361-19 using STREAMS
```

### Example 2: Evaluating a paper with automatic checklist selection

```
Check the paper 'Exploration of the Biosynthetic Potential of the Populus Microbiome' https://journals.asm.org/doi/10.1128/msystems.00045-18
```
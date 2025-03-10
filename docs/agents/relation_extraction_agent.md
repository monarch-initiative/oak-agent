# Relation Extraction Agent

The Relation Extraction Agent extracts structured relationships from scientific papers, focusing on the main contributions, findings, and claims presented in the research.

## Overview

The agent processes PDF documents containing scientific papers and extracts meaningful relations in the form of triples (subject-predicate-object) with supporting evidence. It focuses on capturing the main scientific contributions of papers while maintaining metadata about the source.

## Key Features

- Processes local directories of PDF files
- Extracts structured relations (triples) with evidence
- Caches processed papers to avoid redundant work
- Maintains metadata about source papers
- Supports export of relations to various formats

## Relation Types

The agent extracts various types of relations, including:

- Causal relationships (X causes Y)
- Correlational relationships (X is associated with Y)
- Functional relationships (X performs function Y)
- Compositional relationships (X is composed of Y)
- Regulatory relationships (X regulates Y)

## Usage

### Command Line Interface

```bash
python -m aurelian.agents.relation_extraction.relation_extraction_agent --pdf_directory /path/to/pdfs --cache_directory /path/to/cache
```

### Python API

```python
from aurelian.agents.relation_extraction.relation_extraction_agent import relation_extraction_agent
from aurelian.agents.relation_extraction.relation_extraction_config import RelationExtractionDependencies
from pydantic_ai.chat import ChatMessage

# Create dependencies
deps = RelationExtractionDependencies(
    pdf_directory="/path/to/pdfs",
    cache_directory="/path/to/cache"
)

# Use the agent
response = await relation_extraction_agent.chat(
    messages=[ChatMessage(role="user", content="Process all unprocessed papers")],
    dependencies=deps
)
```

### Gradio Interface

```bash
python -m aurelian.agents.relation_extraction.relation_extraction_gradio
```

## Examples

### Basic Relation Extraction

```
User: List all the PDF files in the configured directory.
Agent: Found 5 PDF files: paper1.pdf, paper2.pdf, paper3.pdf, paper4.pdf, paper5.pdf.
       2 have been processed already.

User: Process the unprocessed papers.
Agent: Processing 3 papers... Done!
       Extracted 27 relations from the papers.

User: Show me the relations about CRISPR.
Agent: Found 3 relations mentioning CRISPR:
       1. CRISPR-Cas9 -> edits -> genomic DNA
       2. CRISPR -> increases -> gene editing precision
       3. Guide RNA -> directs -> CRISPR-Cas9 complex
```

### Relation Analysis

```
User: What's the most common relationship type in the extracted relations?
Agent: The most common relationship type is "increases" with 12 instances, 
       followed by "inhibits" with 8 instances.

User: Export all relations to JSON.
Agent: Exported 27 relations to relations.json.
```

## Data Model

Each extracted relation contains:

- **subject**: The entity or concept that is the source of the relation
- **predicate**: The type of relationship
- **object**: The entity or concept that is the target of the relation
- **evidence**: The specific text from which this relation was extracted
- **confidence**: Confidence score for the extraction (0-1)
- **paper_doi**: DOI of the source paper
- **paper_title**: Title of the source paper
- **paper_authors**: List of authors
- **paper_year**: Publication year
- **section**: Section of the paper where the relation was found
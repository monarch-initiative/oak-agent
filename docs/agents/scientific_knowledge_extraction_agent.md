# Scientific Knowledge Extraction Agent

The Scientific Knowledge Extraction Agent extracts structured knowledge from scientific papers, focusing on the main contributions, findings, and claims presented in the research, and grounds these assertions to standard ontology terms.

## Overview

The agent processes PDF documents containing scientific papers and extracts meaningful scientific assertions in the form of triples (subject-predicate-object) with supporting evidence. It maps these assertions to standard ontology terms to enhance interoperability and integration with knowledge bases. The agent focuses on capturing the main scientific contributions of papers while maintaining comprehensive provenance information.

## Key Features

- Processes local directories of PDF files
- Extracts structured scientific assertions with evidence
- Maps assertions to standard ontology terms
- Maintains complete provenance tracking for scientific assertions
- Caches processed papers to avoid redundant work
- Exports knowledge in various formats including RDF with ontology URIs

## Assertion Types

The agent extracts various types of scientific assertions, including:

- Causal relationships (X causes Y)
- Correlational relationships (X is associated with Y)
- Functional relationships (X performs function Y)
- Compositional relationships (X is composed of Y)
- Regulatory relationships (X regulates Y)

## Ontology Mapping

The agent maps extracted entities and relationships to standard ontologies:

- **Subject/Object Mapping**:
  - Gene Ontology (GO) for biological processes, cellular components, molecular functions
  - ChEBI for chemical entities
  - Disease Ontology (DOID) for diseases
  - Protein Ontology (PR) for proteins
  - Uberon for anatomical entities
  - Cell Ontology (CL) for cell types

- **Predicate Mapping**:
  - Relation Ontology (RO) for relationship types
  - Consistent predicates like "increases", "inhibits", "regulates", etc.
  - Standardized using common scientific relationship terminology

## Usage

### Command Line Interface

```bash
python -m aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_agent --pdf_directory /path/to/pdfs --cache_directory /path/to/cache
```

### Python API

```python
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_agent import scientific_knowledge_extraction_agent
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from pydantic_ai.chat import ChatMessage

# Create dependencies
deps = ScientificKnowledgeExtractionDependencies(
    pdf_directory="/path/to/pdfs",
    cache_directory="/path/to/cache"
)

# Use the agent
response = await scientific_knowledge_extraction_agent.chat(
    messages=[ChatMessage(role="user", content="Process all unprocessed papers")],
    dependencies=deps
)
```

### Gradio Interface

```bash
python -m aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_gradio
```

## Examples

### Basic Knowledge Extraction

```
User: List all the PDF files in the configured directory.
Agent: Found 5 PDF files: paper1.pdf, paper2.pdf, paper3.pdf, paper4.pdf, paper5.pdf.
       2 have been processed already.

User: Process the unprocessed papers.
Agent: Processing 3 papers... Done!
       Extracted 27 scientific assertions from the papers.

User: Show me the assertions about CRISPR.
Agent: Found 3 assertions mentioning CRISPR:
       1. CRISPR-Cas9 -> edits -> genomic DNA
       2. CRISPR -> increases -> gene editing precision
       3. Guide RNA -> directs -> CRISPR-Cas9 complex
```

### Ontology Mapping

```
User: Map all extracted assertions to ontology terms.
Agent: Mapped 22 out of 27 assertions to ontology terms (81.5% mapping rate).
       - 18 subjects mapped (66.7%)
       - 25 predicates mapped (92.6%)
       - 16 objects mapped (59.3%)

User: Show me the mapped assertion for CRISPR-Cas9.
Agent: CRISPR-Cas9 (PR:000050359) -> causally upstream of, positive effect (RO:0002304) -> genomic DNA (CHEBI:33697)
       Evidence: "CRISPR-Cas9 efficiently edits genomic DNA in various cell types."
       Source: Smith et al., 2019 (DOI: 10.1038/s41586-019-1234-5)
```

### RDF Export

```
User: Export assertions as RDF with provenance.
Agent: Successfully exported 22 assertions as RDF triples.
       File saved to: knowledge.rdf
       
User: What's in the RDF export?
Agent: The RDF export contains:
       - Standardized triples using ontology URIs
       - Provenance information (paper source, evidence text)
       - Confidence scores
       - Complete metadata about the extraction
```

## Data Model

Each extracted scientific assertion contains:

### Core Triple
- **subject**: The entity or concept that is the source of the assertion
- **predicate**: The type of relationship
- **object**: The entity or concept that is the target of the assertion

### Ontology Mapping
- **subject_ontology_id**: Ontology identifier for the subject (e.g., "GO:0006915")
- **subject_ontology_label**: Standard label from the ontology
- **subject_ontology_source**: Source ontology (e.g., "GO", "CHEBI", "DOID")
- **predicate_ontology_id**: Ontology identifier for the predicate (e.g., "RO:0002212")
- **predicate_ontology_label**: Standard label from the ontology
- **predicate_ontology_source**: Source ontology (typically "RO")
- **object_ontology_id**: Ontology identifier for the object
- **object_ontology_label**: Standard label from the ontology
- **object_ontology_source**: Source ontology

### Evidence and Provenance
- **evidence**: The specific text from which this assertion was extracted
- **confidence**: Confidence score for the extraction (0-1)
- **paper_doi**: DOI of the source paper
- **paper_title**: Title of the source paper
- **paper_authors**: List of authors
- **paper_year**: Publication year
- **paper_pmid**: PubMed ID if available
- **section**: Section of the paper where the assertion was found
- **extraction_date**: When the assertion was extracted
- **extraction_method**: Method used for extraction
- **sentence_location**: Approximate location of the evidence sentence in the document
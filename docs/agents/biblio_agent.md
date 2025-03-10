# Biblio Agent

The Biblio Agent helps organize and search bibliographic data and citations. It provides tools for searching a bibliography database, retrieving scientific publications, and accessing web content.

## Features

- Search a bibliography database for relevant entries
- Retrieve publication content using PubMed IDs
- Search the web for additional information
- Retrieve web page content for detailed analysis
- Format results with bioregistry links and markdown tables

## Usage

### Python API

```python
from aurelian.agents.biblio import biblio_agent, get_config

# Initialize dependencies
deps = get_config()

# Search for publications about a specific topic
result = await biblio_agent.run(
    "What patients have liver disease?",
    deps=deps
)

# Get the search results
print(result.data)
```

### Command Line Interface

```bash
aurelian biblio "What patients have liver disease?"
```

### Gradio Interface

```python
from aurelian.agents.biblio import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The Biblio Agent provides the following tools:

### search_bibliography

Performs a retrieval search over the biblio database. The query can be any text, such as the name of a disease, phenotype, gene, etc.

### lookup_pmid

Retrieves the full text or abstract of a publication using its PubMed ID (format: "PMID:nnnnnnn").

### search_web

Searches the web using a text query and returns matching web pages with summaries.

### retrieve_web_page

Fetches the contents of a specific web page.

## Examples

### Example 1: Searching for publications about a specific disease

```
What patients have liver disease?
```

### Example 2: Searching for publications involving specific genes

```
What biblio involve genes from metabolic pathways?
```

### Example 3: Analyzing genotype-phenotype relationships

```
How does the type of variant affect phenotype in peroxisomal disorders?
```

### Example 4: Examining publications on a specific condition

```
Examine biblio for skeletal dysplasias, check them against publications
```
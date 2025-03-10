# RAG Agent

The RAG (Retrieval-Augmented Generation) Agent provides a natural language interface for exploring and searching document collections. It uses RAG techniques to combine search capabilities with generative AI to produce relevant, context-aware responses based on document content.

## Features

- Search document collections with natural language queries
- Inspect specific documents by title or other identifying information
- Retrieve PubMed publications via PMID
- Perform web searches and retrieve web page content
- Generate context-aware responses based on document content

## Usage

### Python API

```python
from aurelian.agents.rag import rag_agent, get_config

# Initialize dependencies with your database path and collection
deps = get_config(db_path="sqlite:///path/to/db", collection_name="main")

# Search for documents about a specific topic
result = await rag_agent.run(
    "What papers in collection are relevant to microbial nitrogen fixation?",
    deps=deps
)

# Get the search results
print(result.data)
```

### Command Line Interface

```bash
aurelian rag --db-path "sqlite:///path/to/db" --collection-name "main" "What papers in collection are relevant to microbial nitrogen fixation?"
```

### Gradio Interface

```python
from aurelian.agents.rag import chat

# Launch Gradio interface with your database configuration
interface = chat(db_path="sqlite:///path/to/db", collection_name="main")
interface.launch()
```

## Tools

The RAG Agent provides the following tools:

### search_documents

Performs a retrieval search over the document database using a natural language query. Returns matching documents with relevancy scores.

### inspect_document

Retrieves the full content of a specific document identified by title or other identifying information.

### lookup_pmid

Retrieves the full text or abstract of a publication using its PubMed ID (format: "PMID:nnnnnnn").

### search_web

Searches the web using a text query and returns matching web pages with summaries.

### retrieve_web_page

Fetches the contents of a specific web page.

## Configuration

The RAG Agent requires a document database to function. You can configure it through:

- Environment variables:
  - `AURELIAN_RAG_DB_PATH`: Path to the document database
  - `AURELIAN_RAG_COLLECTION`: Name of the collection (default: "main")
  
- Direct configuration:
  - Pass `db_path` and `collection_name` parameters to `get_config()`

## Examples

### Example 1: Searching for papers on a specific topic

```
What papers in collection are relevant to microbial nitrogen fixation?
```

### Example 2: Finding papers that mention specific genes

```
Find documents that discuss the role of nif genes in nitrogen fixation
```

### Example 3: Summarizing a specific document

```
Summarize the paper titled "Recent advances in nitrogen fixation"
```
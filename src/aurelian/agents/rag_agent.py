from dataclasses import dataclass, field
from typing import Dict, List, Optional

from linkml_store import Client
from linkml_store.api import Collection
from pydantic_ai import Agent, RunContext

from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import flatten
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search

COLLECTION_NAME = "main"


@dataclass
class RagDependencies:
    db_path: str
    collection_name: str
    max_results: int = field(default=10)
    max_content_len: int = 5000
    _collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            client = Client()
            db_path = self.db_path
            client.attach_database(db_path)
            db = client.databases[db_path]
            self._collection = db.get_collection(self.collection_name)
        return self._collection


rag_agent = Agent(
    model="openai:gpt-4o",
    deps_type=RagDependencies,
    result_type=str,
    system_prompt=(
        "You are an AI assistant that help explore a literature collection via RAG."
        " You can use different functions to access the store, for example:"
        "  - `search_documents` to find documents by text query"
        "  - `inspect_document` to retrieve a specific document (by title/name)"
        "You can also use `lookup_pmid` to retrieve the text of a PubMed ID, or `search_web` to search the web."

    ),
)


@rag_agent.tool
def search_documents(ctx: RunContext[RagDependencies], query: str) -> List[Dict]:
    """Performs a retrieval search over the rag database.

    The query can be any text, such as name of a disease, phenotype, gene, etc.
    """
    print(f"SEARCH: {query}")
    qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
    objs = []
    for score, row in qr.ranked_rows:
        row["content"] = row["content"][:ctx.deps.max_content_len]
        obj = flatten(row)
        obj["relevancy_score"] = score
        objs.append(obj)
        print(f"RESULT: {obj}")
    return objs


@rag_agent.tool
def inspect_document(ctx: RunContext[RagDependencies], query: str) -> List[Dict]:
    """Returns the content of the document.

    Args:
        query: E.g. title
    """
    print(f"SEARCH: {query}")
    qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
    objs = []
    for score, row in qr.ranked_rows:
        return row["content"]



@rag_agent.tool_plain
def lookup_pmid(pmid: str) -> str:
    """Lookup the text of a PubMed ID, using its PMID.

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).

    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should be be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve examine the `externalReferences`
    field.

    Returns: full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    return get_pmid_text(pmid)


@rag_agent.tool_plain()
def search_web(query: str) -> str:
    """Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)


@rag_agent.tool_plain
def retrieve_web_page(url: str) -> str:
    """Fetch the contents of a web page.

    Returns:
        The contents of the web page.

    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su

    return su.retrieve_web_page(url)


def chat(model=None, **kwargs):
    import gradio as gr

    deps = RagDependencies(**kwargs)

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: rag_agent.run_sync(query, deps=deps, model=model))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Rag AI Assistant",
        examples=[
            ["What papers in collection are relevant to microbial nitrogen fixation?"],
        ],
    )

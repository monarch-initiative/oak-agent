from dataclasses import dataclass, field
from typing import List, Dict, Optional

from linkml_store import Client
from linkml_store.api import Collection
from pydantic_ai import Agent, RunContext, AgentRunError

from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import flatten
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search

HANDLE = "mongodb://localhost:27017/biblio"
DB_NAME = "biblio"
COLLECTION_NAME = "main"


@dataclass
class BiblioDependencies:
    max_results: int = field(default=10)
    _collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            client = Client()
            client.attach_database(HANDLE, alias=DB_NAME)
            db = client.databases[DB_NAME]
            self._collection = db.get_collection(COLLECTION_NAME)
        return self._collection

biblio_agent = Agent(
    model="openai:gpt-4o",
    deps_type=BiblioDependencies,
    result_type=str,
    system_prompt=(
        "You are an AI assistant that help organize a bibliography."
        " You can use different functions to access the store, for example:"
        "  - `search` to find biblio by text query"
        "  - `lookup_phenopacket` to retrieve a specific phenopacket by ID"
        "You can also use `lookup_pmid` to retrieve the text of a PubMed ID, or `search_web` to search the web."
        "While you are knowledgeable about clinical genetics, you should always use the store and "
        "functions provided to answer questions, rather than providing your own opinion or knowledge,"
        " unless explicitly asked. For example, if you are asked to 'review' something then you "
        "can add your own perspective and understanding. "
        "You should endeavour to provide answers in narrative form that would be understood "
        "by a clinical geneticists, but provide backup using assertions from the store."
        " providing IDs of terms alongside labels is encouraged, unless asked not to."
        "Stick to markdown, and all prefixed IDs should by hyperlinked with bioregistry,"
        " i.e https://bioregistry.io/{curie}."
        "tables are a good way of summarizing or comparing multiple patients, use markdown"
        " tables for this. Use your judgment in how to roll up tables, and whether values"
        " should be present/absent, increased/decreased, or more specific."
    )
)

@biblio_agent.tool
def search_bibliography(ctx: RunContext[BiblioDependencies], query: str) -> List[Dict]:
    """
    Performs a retrieval search over the biblio database.

    The query can be any text, such as name of a disease, phenotype, gene, etc.

    The objects returned are "biblio" which is a structured representation
    of a patient. Each is uniquely identified by a phenopacket ID (essentially
    the patient ID).

    The objects returned are summaries of biblio; omit some details such
    as phenotypes. Use `lookup_biblio` to retrieve full details of a phenopacket.

    Note that the phenopacket store may not be complete, and the retrieval
    method may be imperfect
    """
    print(f"SEARCH: {query}")
    qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
    objs = []
    for score, row in qr.ranked_rows:
        obj = flatten(row, preserve_keys=["interpretations", "diseases"])
        obj["relevancy_score"] = score
        objs.append(obj)
        print(f"RESULT: {obj}")
    return objs


@biblio_agent.tool_plain
def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).

    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should be be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve examine the `externalReferences`
    field.

    Returns: full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    return get_pmid_text(pmid)


@biblio_agent.tool_plain()
def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@biblio_agent.tool_plain
def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Returns:
        The contents of the web page.
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    return su.retrieve_web_page(url)


def chat(**kwargs):
    import gradio as gr
    deps = BiblioDependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: biblio_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="biblio AI Assistant",
        examples=[
            ["What patients have liver disease?"],
            ["What biblio involve genes from metabolic pathways"],
            ["How does the type of variant affect phenotype in peroxisomal disorders?"],
            ["Examine biblio for skeletal dysplasias, check them against publications"],
        ]
    )

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from pydantic_ai import Agent, RunContext, AgentRunError

from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import flatten
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search

HANDLE = "mongodb://localhost:27017/phenopackets"
DB_NAME = "phenopackets"
COLLECTION_NAME = "main"


@dataclass
class DiagnosisDependencies:
    pass

diagnosis_agent = Agent(
    model="openai:gpt-4o",
    deps_type=DiagnosisDependencies,
    result_type=str,
    system_prompt=(
        "You are an expert clinical geneticist."
        " Your task is to assist in diagnosing rare diseases, and determining underlying gene"
        "Stick to markdown, and all prefixed IDs should by hyperlinked with bioregistry,"
        " i.e https://bioregistry.io/{curie}."
    )
)

@diagnosis_agent.tool
def find_disease_id(ctx: RunContext[DiagnosisDependencies], query: str) -> List[Dict]:
    """
    Performs a retrieval search over the Phenopackets database.

    The query can be any text, such as name of a disease, phenotype, gene, etc.

    The objects returned are "Phenopackets" which is a structured representation
    of a patient. Each is uniquely identified by a phenopacket ID (essentially
    the patient ID).

    The objects returned are summaries of Phenopackets; omit some details such
    as phenotypes. Use `lookup_Phenopackets` to retrieve full details of a phenopacket.

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

@diagnosis_agent.tool
def lookup_phenopacket(ctx: RunContext[DiagnosisDependencies], phenopacket_id: str) -> Dict:
    """
    Performs a lookup of an individual Phenopackets model by its ID

    IDs are typically of the form PMID_nnn_PatientNumber, but this should be be assumed.

    Args:
        phenopacket_id: The ID of the Phenopacket

    """
    print(f"LOOKUP: {phenopacket_id}")
    qr = ctx.deps.collection.find({"id": phenopacket_id})
    if not qr.rows:
        print(f"Could not find model with ID {phenopacket_id}")
        return None
        #raise ValueError(f"Could not find model with ID {phenopacket_id}")
    return qr.rows[0]

@diagnosis_agent.tool_plain
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


@diagnosis_agent.tool_plain()
def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@diagnosis_agent.tool_plain
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
    deps = DiagnosisDependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: diagnosis_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Diagnosis AI Assistant",
        examples=[
        ]
    )

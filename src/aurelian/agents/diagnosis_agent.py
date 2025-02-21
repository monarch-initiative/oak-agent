import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from oaklib import get_adapter
from oaklib.datamodels.search import create_search_configuration
from pydantic_ai import Agent, RunContext, AgentRunError

from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import flatten
from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search

HANDLE = "mongodb://localhost:27017/phenopackets"
DB_NAME = "phenopackets"
COLLECTION_NAME = "main"

mondo_adapter = get_adapter("sqlite:obo:mondo")


@dataclass
class DiagnosisDependencies:
    max_search_results: int = 10

diagnosis_agent = Agent(
    model="openai:gpt-4o",
    deps_type=DiagnosisDependencies,
    result_type=str,
    system_prompt=(
        "You are an expert clinical geneticist."
        " Your task is to assist in diagnosing rare diseases,"
        " and with determining underlying gene or variant."
        " The recommended workflow is to first think of a set of candidate diseases."
        "You can find the Mondo ID of the disease using the `find_disease_id` function."
        " You can query the Monarch knowledge base to get a list of phenotypes for that"
        " disease id. You can use this to check your initial hypothesis."
        "Stick to markdown, and all prefixed IDs should by hyperlinked with bioregistry,"
        " i.e https://bioregistry.io/{curie}."
    )
)


@diagnosis_agent.tool
def find_disease_id(ctx: RunContext[DiagnosisDependencies], query: str) -> List[Dict]:
    """
    Finds the disease ID for a given search term
    """
    return search_ontology(mondo_adapter, query, limit=ctx.deps.max_search_results)


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

import asyncio
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Dict, Optional

from oaklib import get_adapter
from oaklib.datamodels.search import create_search_configuration
from oaklib.implementations import MonarchImplementation
from pydantic_ai import Agent, RunContext, AgentRunError

from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import flatten, obj_to_dict
from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search

HANDLE = "mongodb://localhost:27017/phenopackets"
DB_NAME = "phenopackets"
COLLECTION_NAME = "main"

HAS_PHENOTYPE = "biolink:has_phenotype"

monarch_adapter = MonarchImplementation()

@lru_cache
def get_mondo_adapter():
    return get_adapter("sqlite:obo:mondo")


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
        " You should show your reasoning, and your candidate list (as many as appropriate)."
        " You should then check your hypotheses against the Monarch knowledge base."
        "You can find the Mondo ID of the disease using the `find_disease_id` function."
        " You should then query the Monarch knowledge base to get a list of phenotypes for that"
        " disease id, using the `find_disease_phenotypes` function."
        " Present results in detail, using markdown tables unless otherwise specified."
        " Try and account for all presented patient phenotypes in the table (you can"
        " roll up similar phenotypes to broader categories)."
        " also try and account for hallmark features of the disease not found in the patient,"
        " always showing your reasoning."
        " if you get something from a web search, tell me the web page."
        " if you get something from the knowledge base, give provenance."
        " again, using information from the knowledge base."
        " Give detailed provenance chains in <details> tags."
        " Show ontology term IDs together with labels whenever possible."
        " Include HPO IDs which you will get from the `find_disease_phenotypes` function"
        " (never guess these, always get from the query results)"
        "Stick to markdown, and all prefixed IDs should by hyperlinked with bioregistry,"
        " i.e https://bioregistry.io/{curie}."
    )
)


@diagnosis_agent.tool
def find_disease_id(ctx: RunContext[DiagnosisDependencies], query: str) -> List[Dict]:
    """
    Finds the disease ID for a given search term.

    OAK search term syntax is used; the default strategy is to match
    label:

        ```
        find_disease_id("Dravet syndrome")
        ```

    You can use OAK expressions, e.g, all labels
    that start with "Peroxisomal biogenesis disorder":

        ```
        find_disease_id("l^Peroxisomal biogenesis disorder")
        ```

    Args:
        query: The label search term to use
    """
    print(f"Disease Search: {query}")
    return search_ontology(get_mondo_adapter(), query, limit=ctx.deps.max_search_results)


@diagnosis_agent.tool
def find_disease_phenotypes(ctx: RunContext[DiagnosisDependencies], query: str) -> List[Dict]:
    """
    Finds the phenotypes for a disease ID

    Example:

        ```
        find_disease_phenotypes("MONDO:0007947")
        ```

    Args:
        query: The disease ID to search for (should be ID but can be name)
    Returns:
        List of phenotypes for the disease
    """
    print(f"Phenotype query: {query}")
    if ":" in query:
        query_ids = [query]
    else:
        query_ids = find_disease_id(ctx, query)
    if not query_ids:
        raise AgentRunError(f"Could not find disease for query: {query}")
    results = [obj_to_dict(x) for x in monarch_adapter.associations(subjects=query_ids, predicates=[HAS_PHENOTYPE])]
    print(f"Results[{query_ids}]: {results}")
    return results


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
            """Patient has growth failure, distinct facial features, alopecia, and skin aging.
                        Findings excluded: Pigmented nevi, cafe-au-lait spots, and photosensitivity.
                        Onset was in infancy.
                        Return diagnosis with MONDO ID""",
            "what eye phenotypes does Marfan syndrome have?",
            "What is the ID for Ehlers-Danlos syndrome type 1?",
            "What are the kinds of Ehlers-Danlos syndrome?",
            "Look at phenotypes for Ehler Danlos classic type 2. Do a literature search to look at latest studies. What is missing from the KB?",

        ]
    )

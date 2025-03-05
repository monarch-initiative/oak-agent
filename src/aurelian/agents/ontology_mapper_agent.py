"""Agent for creating ontology mappings.
"""
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Dict, Union

from oaklib import get_adapter
from pydantic_ai import Agent, RunContext

from aurelian.utils.async_utils import run_sync
from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.search_utils import web_search


@lru_cache
def get_ontology_adapter(ont: str):
    ont = ont.lower()
    return get_adapter(f"sqlite:obo:{ont}")


@dataclass
class OntologyDependencies:
    """
    Configuration for the ontology mapper agent.

    We include a default set of ontologies because the initial text embedding index is slow..
    this can easily be changed e.g. in command line
    """
    max_search_results: int = 30
    ontologies: List[str] = field(default_factory=lambda: ["mondo", "hp", "go", "uberon", "cl", "mp", "envo"])


ontology_mapper_agent = Agent(
    model="openai:gpt-4o",
    deps_type=OntologyDependencies,
    result_type=str,
    system_prompt=(
        "You are an expert on OBO ontologies."
        " Your task is to assist the user in finding the relevant ontology terms,"
        " given inputs such as search queries, lists of terms to map, alternate ontology classes, etc."
        " You have access to a limited set of ontologies, which you can search using the `search_terms` function."
        " This uses embedding-based search, so you can use partial terms, alternate names, etc."
        " You can also expand the users search terms as appropriate, making use of any context provided."
        " You should show your reasoning, and your candidate list (as many as appropriate)."
        " Do not be completely literal in the task of matching ontology terms. If something seems out of scope"
        " for an ontology, give the appropriate response and recommendation. "
        " If a term is in scope and can't be found, suggest a term request."
        " Give detailed provenance chains in <details> tags."
        " Show ontology term IDs together with labels whenever possible."
        " IMPORTANT: precision is important. If a user makes a query for a term then you should only return terms"
        " that represent the SAME CONCEPT. Sometimes this will not be possible, and only close concepts can be found."
        " Here you can report the close terms, but make it clear these are NOT THE SAME. Before doing this, you should"
        " try strategies like varying your search term, based on your knowledge of that ontology"
        " You must NEVER guess ontology term IDs, the query results should always be the source of truth."
        "Stick to markdown, and all prefixed IDs should by hyperlinked with bioregistry,"
        " i.e https://bioregistry.io/{curie}."
    )
)

@ontology_mapper_agent.system_prompt
def add_ontologies(ctx: RunContext[OntologyDependencies]) -> str:
    allowed_ontologies = ctx.deps.ontologies
    if allowed_ontologies:
        return f"Allowed ontologies: {allowed_ontologies}"
    return "Use any ontology (ideally in OBO repository)"


@ontology_mapper_agent.tool
def search_terms(ctx: RunContext[OntologyDependencies], ontology_id: str, query: str) -> List[Dict]:
    """
    Finds similar ontology terms to the search query.

    For example:

        ```
        search_terms("go", "cycle cycle and related processes")
        ```

    Relevancy ranking is used, with semantic similarity, which means
    queries need only be close in semantic space. E.g. while GO does not
    deal with diseases, this may return relevant pathways or structures:

        ```
        search_terms("go", "terms most relevant to Parkinson disease")
        ```

    Args:

        ontology_id: The ontology ID to search in (e.g. cl, go, uberon)
        query: The search query
    """
    print(f"Term Search: {ontology_id} {query}")
    if " " in ontology_id:
        return "Invalid ontology ID, use an OBO style ID like cl, mondo, chebi, etc."
    return search_ontology(get_ontology_adapter(ontology_id), query, limit=ctx.deps.max_search_results)


@ontology_mapper_agent.tool_plain()
def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@ontology_mapper_agent.tool_plain
def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Returns:
        The contents of the web page.
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    return su.retrieve_web_page(url)


def chat(deps: OntologyDependencies, **kwargs):
    import gradio as gr

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: ontology_mapper_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Ontology mapper AI Assistant",
        examples=[
            "Find the term in the cell ontology for neuron",
            "Best terms to use for the middle 3 fingers",
            "What is the term for the process of cell division in GO?",
            """
            Find good MP terms for the following. If no matches can be found, suggest appropriate action

            * CA1 TBS Reduced
            * CA1 TBS Increased
            * Surface righting Reduced
            * Contextual fear conditioning (shock context/context shock) Reduced
            * Morris water maze Reduced
            * Rotarod Increased
            * Rotarod Reduced
            """,
        ]
    )

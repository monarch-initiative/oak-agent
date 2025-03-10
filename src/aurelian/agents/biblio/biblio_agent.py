"""
Agent for working with bibliographies and citation data.
"""
from pydantic_ai import Agent, RunContext

from .biblio_config import BiblioDependencies
from .biblio_tools import search_bibliography, lookup_pmid, search_web, retrieve_web_page


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
    ),
)


@biblio_agent.tool
async def search_bibliography_tool(ctx: RunContext[BiblioDependencies], query: str):
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
    return await search_bibliography(ctx, query)


@biblio_agent.tool
async def lookup_pmid_tool(ctx: RunContext[BiblioDependencies], pmid: str):
    """
    Lookup the text of a PubMed ID, using its PMID.

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).

    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should be be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve examine the `externalReferences`
    field.

    Returns: full text if available, otherwise abstract
    """
    return await lookup_pmid(ctx, pmid)


@biblio_agent.tool
async def search_web_tool(ctx: RunContext[BiblioDependencies], query: str):
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    return await search_web(ctx, query)


@biblio_agent.tool
async def retrieve_web_page_tool(ctx: RunContext[BiblioDependencies], url: str):
    """
    Fetch the contents of a web page.

    Returns:
        The contents of the web page.
    """
    return await retrieve_web_page(ctx, url)
"""
Agent for retrieval-augmented generation (RAG) against document collections.
"""
from pydantic_ai import Agent, RunContext

from .rag_config import RagDependencies
from .rag_tools import search_documents, inspect_document, lookup_pmid, search_web, retrieve_web_page


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
async def search_documents_tool(ctx: RunContext[RagDependencies], query: str):
    """
    Performs a retrieval search over the RAG database.
    
    The query can be any text, such as name of a disease, phenotype, gene, etc.
    """
    return await search_documents(ctx, query)


@rag_agent.tool
async def inspect_document_tool(ctx: RunContext[RagDependencies], query: str):
    """
    Returns the content of the document.
    
    Args:
        query: E.g. title
    """
    return await inspect_document(ctx, query)


@rag_agent.tool
async def lookup_pmid_tool(ctx: RunContext[RagDependencies], pmid: str):
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


@rag_agent.tool
async def search_web_tool(ctx: RunContext[RagDependencies], query: str):
    """
    Search the web using a text query.
    
    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.
    
    Returns: matching web pages plus summaries
    """
    return await search_web(ctx, query)


@rag_agent.tool
async def retrieve_web_page_tool(ctx: RunContext[RagDependencies], url: str):
    """
    Fetch the contents of a web page.
    
    Returns:
        The contents of the web page.
    """
    return await retrieve_web_page(ctx, url)
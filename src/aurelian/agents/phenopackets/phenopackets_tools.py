"""
Tools for the phenopackets agent.
"""
from typing import List, Dict, Optional

from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.phenopackets.phenopackets_config import PhenopacketsDependencies
from aurelian.utils.data_utils import flatten
from aurelian.agents.literature.literature_tools import (
    lookup_pmid as literature_lookup_pmid,
    search_literature_web,
    retrieve_literature_page
)


async def search_phenopackets(ctx: RunContext[PhenopacketsDependencies], query: str) -> List[Dict]:
    """
    Performs a retrieval search over the Phenopackets database.

    The query can be any text, such as name of a disease, phenotype, gene, etc.

    The objects returned are "Phenopackets" which is a structured representation
    of a patient. Each is uniquely identified by a phenopacket ID (essentially
    the patient ID).

    The objects returned are summaries of Phenopackets; some details such
    as phenotypes are omitted. Use `lookup_phenopacket` to retrieve full details.

    Args:
        ctx: The run context
        query: The search query text

    Returns:
        List[Dict]: List of phenopackets matching the query
    """
    print(f"SEARCH PHENOPACKETS: {query}")
    try:
        qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
        objs = []
        for score, row in qr.ranked_rows:
            obj = flatten(row, preserve_keys=["interpretations", "diseases"])
            obj["relevancy_score"] = score
            objs.append(obj)
            print(f"RESULT: {obj}")
        
        if not objs:
            raise ModelRetry(f"No phenopackets found matching the query: {query}. Try a different search term.")
        
        return objs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching phenopackets: {str(e)}")


async def lookup_phenopacket(ctx: RunContext[PhenopacketsDependencies], phenopacket_id: str) -> Dict:
    """
    Performs a lookup of an individual Phenopacket by its ID.

    IDs are typically of the form PMID_nnn_PatientNumber, but this should not be assumed.

    Args:
        ctx: The run context
        phenopacket_id: The ID of the Phenopacket to look up

    Returns:
        Dict: The phenopacket data
    """
    print(f"LOOKUP PHENOPACKET: {phenopacket_id}")
    try:
        qr = ctx.deps.collection.find({"id": phenopacket_id})
        if not qr.rows:
            raise ModelRetry(f"Could not find phenopacket with ID {phenopacket_id}. The ID may be incorrect.")
        return qr.rows[0]
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error looking up phenopacket {phenopacket_id}: {str(e)}")


async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed article by its PMID.
    
    A PMID should be of the form "PMID:nnnnnnn" (no underscores).
    
    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should not be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve and examine the `externalReferences` field.
    
    Args:
        pmid: The PubMed ID to look up
        
    Returns:
        str: Full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID FOR PHENOPACKET: {pmid}")
    return await literature_lookup_pmid(pmid)


async def search_web(query: str) -> str:
    """
    Search the web using a text query.
    
    Args:
        query: The search query
        
    Returns:
        str: Search results with summaries
    """
    print(f"PHENOPACKET WEB SEARCH: {query}")
    return await search_literature_web(query)


async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.
    
    Args:
        url: The URL to fetch
        
    Returns:
        str: The contents of the web page
    """
    print(f"FETCH WEB PAGE FOR PHENOPACKET: {url}")
    return await retrieve_literature_page(url)
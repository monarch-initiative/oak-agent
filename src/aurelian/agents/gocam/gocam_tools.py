"""
Tools for the GOCAM agent.
"""
from typing import List, Dict, Optional

from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.uniprot.uniprot_tools import normalize_uniprot_id
from aurelian.utils.data_utils import flatten
from aurelian.agents.literature.literature_tools import search_literature_web, retrieve_literature_page


async def search_gocams(ctx: RunContext[GOCAMDependencies], query: str) -> List[Dict]:
    """
    Performs a retrieval search over the GO-CAM database.

    The query can be any text, such as name of a pathway, genes, or
    a complex sentence.

    The objects returned are summaries of GO-CAM models; they do not contain full
    details. Use `lookup_gocam` to retrieve full details of a model.

    This tool uses a retrieval method that is not guaranteed to always return
    complete results, and some results may be less relevant than others.
    You MAY use your judgment in filtering these.

    Args:
        ctx: The run context
        query: The search query text

    Returns:
        List[Dict]: List of GOCAM models matching the query
    """
    print(f"SEARCH GOCAMS: {query}")
    try:
        qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
        objs = []
        for score, row in qr.ranked_rows:
            obj = flatten(row)
            obj["relevancy_score"] = score
            objs.append(obj)
            print(f"RESULT: {obj}")

        if not objs:
            raise ModelRetry(f"No GOCAM models found matching the query: {query}. Try a different search term.")

        return objs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching GOCAM models: {str(e)}")


async def lookup_gocam(ctx: RunContext[GOCAMDependencies], model_id: str) -> Dict:
    """
    Performs a lookup of a GO-CAM model by its ID, and returns the model.

    Args:
        ctx: The run context
        model_id: The ID of the GO-CAM model to look up

    Returns:
        Dict: The GO-CAM model data
    """
    print(f"LOOKUP GOCAM: {model_id}")
    try:
        # Normalize the model ID
        if ":" in model_id:
            parts = model_id.split(":")
            if parts[0] != "gomodel":
                model_id = f"gomodel:{parts[1]}"
        else:
            model_id = f"gomodel:{model_id}"

        qr = ctx.deps.collection.find({"id": model_id})
        if not qr.rows:
            raise ModelRetry(f"Could not find GO-CAM model with ID {model_id}. The ID may be incorrect.")
        return qr.rows[0]
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error looking up GO-CAM model {model_id}: {str(e)}")


async def lookup_uniprot_entry(ctx: RunContext[GOCAMDependencies], uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number.

    This can be used to obtain further information about a protein in
    a GO-CAM.

    Args:
        ctx: The run context
        uniprot_acc: The Uniprot accession

    Returns:
        str: Detailed functional and other info about the protein
    """
    print(f"LOOKUP UNIPROT: {uniprot_acc}")
    try:
        normalized_acc = normalize_uniprot_id(uniprot_acc)
        uniprot_service = ctx.deps.get_uniprot_service()
        result = uniprot_service.retrieve(normalized_acc, frmt="txt")

        if not result or "Error" in result or "Entry not found" in result:
            raise ModelRetry(f"Could not find UniProt entry for {uniprot_acc}. The accession may be incorrect.")

        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving UniProt entry for {uniprot_acc}: {str(e)}")


# These functions have been removed and replaced with direct use of
# literature_lookup_pmid, search_literature_web, and retrieve_literature_page
# from aurelian.agents.literature.literature_tools

from aurelian.utils.search_utils import web_search


async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Args:
        query: Text query

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

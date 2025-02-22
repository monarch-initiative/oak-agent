import re

import requests
from duckduckgo_search import DDGS
from markdownify import markdownify

from aurelian.utils.pubmed_utils import doi_to_pmid, extract_doi_from_url, get_pmcid_text, get_pmid_text

MAX_LENGTH_TRUNCATE_CONTENT = 20000


def web_search(query: str, max_results=10, **kwargs) -> str:
    """Search the web using DuckDuckGo

    Example:
        >>> result = web_search("Winner of 2024 nobel prize in chemistry")
        >>> assert "Baker" in result


    Args:
        query:
        max_results:
        **kwargs:

    Returns:

    """
    ddgs = DDGS(**kwargs)
    results = ddgs.text(query, max_results=max_results)
    if len(results) == 0:
        return "No results found! Try a less restrictive/shorter query."
    postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
    return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


def retrieve_web_page(url: str) -> str:
    """Retrieve the text of a web page.

    Example:
        >>> url = "https://en.wikipedia.org/wiki/COVID-19"
        >>> text = retrieve_web_page(url)
        >>> assert "COVID-19" in text

    PMCs are redirected:

        >>> url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5048378/"
        >>> text = retrieve_web_page(url)
        >>> assert "integrated stress response (ISR)" in text

    URLs with DOIs:

        >>> url = "https://microbiomejournal.biomedcentral.com/articles/10.1186/s40168-020-00889-8"
        >>> text = retrieve_web_page(url)
        >>> assert "photosynthesis" in text

    Args:
        url: URL of the web page

    Returns:
        str: The text of the web page

    """
    if url.startswith("https://pmc.ncbi.nlm.nih.gov/articles/PMC"):
        url = url.strip("/")
        pmc_id = url.split("/")[-1]
        # print(f"REWIRING URL: Fetching PMC ID: {pmc_id}")
        return get_pmcid_text(pmc_id)

    doi = extract_doi_from_url(url)
    if doi:
        # print(f"REWIRING URL: Fetching DOI: {doi}")
        pmid = doi_to_pmid(doi)
        return get_pmid_text(pmid)

    response = requests.get(url, timeout=20)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Convert the HTML content to Markdown
    markdown_content = markdownify(response.text).strip()

    # Remove multiple line breaks
    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

    return truncate_content(markdown_content, 10000)


def truncate_content(content: str, max_length: int = MAX_LENGTH_TRUNCATE_CONTENT) -> str:
    if len(content) <= max_length:
        return content
    else:
        return (
            content[: max_length // 2]
            + f"\n..._This content has been truncated to stay below {max_length} characters_...\n"
            + content[-max_length // 2 :]
        )

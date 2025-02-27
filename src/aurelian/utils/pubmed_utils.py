import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from aurelian.utils.doi_fetcher import DOIFetcher

BIOC_URL = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/ascii"
PUBMED_EUTILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=xml"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"

DOI_PATTERN = r"/(10\.\d{4,9}/[\w\-.]+)"

doi_fetcher = DOIFetcher()


def extract_doi_from_url(url: str) -> Optional[str]:
    """Extracts the DOI from a given journal URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str: The extracted DOI if found, otherwise an empty string.

    """
    doi_match = re.search(DOI_PATTERN, url)
    return doi_match.group(1) if doi_match else None


def doi_to_pmid(doi: str) -> Optional[str]:
    """Converts a DOI to a PMID using the NCBI ID Converter API.

    Args:
        doi (str): The DOI to be converted.

    Returns:
        str: The corresponding PMID if found, otherwise an empty string.

    """
    API_URL = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi}&format=json"
    response = requests.get(API_URL).json()
    records = response.get("records", [])
    pmid = records[0].get("pmid", None) if records else None
    return pmid


def get_doi_text(doi: str) -> str:
    """Fetch the full text of an article using a DOI.

    TODO: non pubmed sources

    Example:
        >>> doi = "10.1128/msystems.00045-18"
        >>> full_text = get_doi_text(doi)
        >>> assert "Populus Microbiome" in full_text

    Args:
        doi: The DOI of the article.

    Returns:
        The full text of the article if available, otherwise an empty string.

    """
    pmid = doi_to_pmid(doi)
    if not pmid:
        info = doi_fetcher.get_full_text(doi)
        if info:
            return info
        else:
            return f"PMID not found for {doi} and not available via unpaywall"
    return get_pmid_text(pmid)


def get_pmid_from_pmcid(pmcid):
    """Fetch the PMID from a PMC ID using the Entrez E-utilities `esummary`.

    Example:
        >>> pmcid = "PMC5048378"
        >>> pmid = get_pmid_from_pmcid(pmcid)
        >>> print(pmid)
        27629041

    Args:
        pmcid:

    Returns:

    """
    if ":" in pmcid:
        pmcid = pmcid.split(":")[1]
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "pmc", "id": pmcid.replace("PMC", ""), "retmode": "json"}  # Remove "PMC" prefix if included

    response = requests.get(url, params=params)
    data = response.json()

    # Extract PMID
    try:
        uid = data["result"]["uids"][0]  # Extract the UID
        article_ids = data["result"][uid]["articleids"]  # Get article IDs
        for item in article_ids:
            if item["idtype"] == "pmid":
                return item["value"]
    except KeyError:
        return "PMID not found"


def get_pmcid_text(pmcid: str) -> str:
    """Fetch full text from PubMed Central Open Access BioC XML.

    Example:
        >>> pmcid = "PMC5048378"
        >>> full_text = get_pmcid_text(pmcid)
        >>> assert "integrated stress response (ISR)" in full_text

    Args:
        pmcid:

    Returns:

    """
    pmid = get_pmid_from_pmcid(pmcid)
    return get_pmid_text(pmid)


def get_pmid_text(pmid: str) -> str:
    """Fetch full text from PubMed Central Open Access BioC XML.
    If full text is not available, fallback to fetching the abstract from PubMed.

    Example:
        >>> pmid = "11"
        >>> full_text = get_pmid_text(pmid)
        >>> print(full_text)
        Identification of adenylate cyclase-coupled beta-adrenergic receptors with radiolabeled beta-adrenergic antagonists.
        <BLANKLINE>
        No abstract available

    Args:
        pmid: PubMed ID of the article.

    Returns:
        The full text of the article if available, otherwise the abstract.

    """
    if ":" in pmid:
        pmid = pmid.split(":")[1]
    text = get_full_text_from_bioc(pmid)
    if not text:
        doi = pmid_to_doi(pmid)
        if doi:
            text = doi_fetcher.get_full_text(doi)
    if not text:
        text = get_abstract_from_pubmed(pmid)
    return text

def pmid_to_doi(pmid: str) -> Optional[str]:
    if ":" in pmid:
        pmid = pmid.split(":")[1]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    response = requests.get(url)
    data = response.json()

    try:
        article_info = data["result"][str(pmid)]
        for aid in article_info["articleids"]:
            if aid["idtype"] == "doi":
                return aid["value"]
        elocationid = article_info.get("elocationid", "")
        if elocationid.startswith("10."):  # DOI starts with "10."
            return elocationid
        else:
            return None
    except KeyError:
        return None


def get_full_text_from_bioc(pmid: str) -> str:
    """Fetch full text from PubMed Central Open Access BioC XML.

    Example:
        >>> pmid = "17299597"
        >>> full_text = get_full_text_from_bioc(pmid)
        >>> assert "Evolution of biological complexity." in full_text

    Args:
        pmid: PubMed ID of the article.

    Returns:
        The full text of the article if available, otherwise an empty string.

    """
    response = requests.get(BIOC_URL.format(pmid=pmid))

    if response.status_code != 200:
        return ""  # Return empty string if request fails

    soup = BeautifulSoup(response.text, "xml")

    # Extract ONLY text from <text> tags within <passage>
    text_sections = [text_tag.get_text() for text_tag in soup.find_all("text")]

    full_text = "\n".join(text_sections).strip()
    return full_text


def get_abstract_from_pubmed(pmid: str) -> str:
    """Fetch the title and abstract of an article from PubMed using Entrez E-utilities `efetch`.

    Example:
        >>> pmid = "31653696"
        >>> abstract = get_abstract_from_pubmed(pmid)
        >>> assert "The apparent deglycase activity of DJ-1" in abstract

    Args:
        pmid: PubMed ID of the article.

    Returns:
        The title and abstract text if available, otherwise an empty string.

    """
    response = requests.get(EFETCH_URL.format(pmid=pmid))

    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "xml")

    # Extract title
    title_tag = soup.find("ArticleTitle")
    title = title_tag.get_text().strip() if title_tag else "No title available"

    # Extract abstract (may contain multiple sections)
    abstract_tags = soup.find_all("AbstractText")
    abstract = "\n".join(tag.get_text().strip() for tag in abstract_tags) if abstract_tags else "No abstract available"

    return f"{title}\n\n{abstract}"

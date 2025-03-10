import os
import re
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Optional

import logfire
import requests
import requests_cache
from bs4 import BeautifulSoup
from markitdown import MarkItDown
from openai import BaseModel
from pydantic import Field


class FullTextInfo(BaseModel):
    """Data model for full text information."""

    success: bool = True
    abstract: Optional[str] = Field(None, description="Abstract of the article")
    text: Optional[str] = Field(None, description="Full text of the article")
    source: Optional[str] = Field(None, description="Source of the full text")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata of the article")
    pdf_url: Optional[str] = Field(None, description="URL to the PDF version of the article")


class DOIFetcher:
    """Fetch metadata and full text for a DOI using various APIs."""

    def __init__(self, email: Optional[str] = None, url_prefixes: Optional[List[str]] = None):
        """Initialize the DOI fetcher with a contact email (required by some APIs).

        Args:
            email (str): Contact email for API access
            url_prefixes (List[str]): List of URL prefixes to check for full text

        """
        self.email = email or os.getenv("EMAIL") or "test@example.com"
        self.url_prefixes = url_prefixes or os.getenv("DOI_FULL_TEXT_URLS", "").split(",")
        self.headers = {"User-Agent": f"DOIFetcher/1.0 (mailto:{email})", "Accept": "application/json"}

    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and normalized characters.

        Args:
            text:

        Returns:
            str: The cleaned text

        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove non-printable characters
        text = "".join(char for char in text if char.isprintable())
        return text.strip()

    def get_metadata(self, doi: str, strict=False) -> Optional[Dict[str, Any]]:
        """Fetch metadata for a DOI using the Crossref API.

        Args:
            doi (str): The DOI to look up
            strict (bool): Raise exceptions if API call fails

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary if successful, None otherwise

        """
        base_url = "https://api.crossref.org/works/"
        try:
            response = requests.get(f"{base_url}{doi}", headers=self.headers)
            response.raise_for_status()
            return response.json()["message"]
        except Exception as e:
            if strict:
                raise e
            logfire.warn(f"Error fetching metadata: {e}")
            return None

    def get_unpaywall_info(self, doi: str, strict=False) -> Optional[Dict[str, Any]]:
        """Check Unpaywall for open access versions.

        Example:
            >>> fetcher = DOIFetcher()
            >>> doi = "10.1038/nature12373"
            >>> unpaywall_data = fetcher.get_unpaywall_info(doi)
            >>> assert unpaywall_data["doi"] == doi
            >>> unpaywall_data["best_oa_location"]["url_for_pdf"]
            'https://europepmc.org/articles/pmc4221854?pdf=render'

        Args:
            doi (str): The DOI to look up
            strict (bool): Raise exceptions if API call fails

        Returns:
            Optional[Dict[str, Any]]: Unpaywall data if successful, None otherwise

        """
        base_url = f"https://api.unpaywall.org/v2/{doi}"
        try:
            response = requests.get(f"{base_url}?email={self.email}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if strict:
                raise e
            logfire.warn(f"Error fetching Unpaywall data: {e}")
            return None

    def get_full_text(self, doi: str, fallback_to_abstract=True) -> Optional[str]:
        """Get the full text of a paper using various methods.

        Example:
            >>> fetcher = DOIFetcher()
            >>> doi = "10.1128/msystems.00045-18"
            >>> full_text = fetcher.get_full_text(doi)
            >>> assert "Populus Microbiome" in full_text

        Args:
            doi:
            fallback_to_abstract:

        Returns:
            str: The full text if available, else abstract text if fallback_to_abstract,
              else None

        """
        info = self.get_full_text_info(doi)
        if not info:
            return None
        text = info.text
        if text:
            return self.clean_text(text)
        if info.pdf_url:
            text = self.text_from_pdf_url(info.pdf_url)
            if text:
                return self.clean_text(text)
        message = "FULL TEXT NOT AVAILABLE"
        if fallback_to_abstract:
            metadata = info.metadata or {}
            abstract = metadata.get("abstract")
            if abstract:
                return self.clean_text(abstract) + f"\n\n{message}"
        return message

    def get_full_text_info(self, doi: str) -> Optional[FullTextInfo]:
        """Attempt to get the full text of a paper using various methods.

            >>> fetcher = DOIFetcher()
            >>> doi = "10.1128/msystems.00045-18"
            >>> info = fetcher.get_full_text_info(doi)
            >>> metadata = info.metadata
            >>> metadata["type"]
            'journal-article'
            >>> metadata["title"][0][0:20]
            'Exploration of the B'
            >>> assert info.pdf_url is not None
            >>> info.pdf_url
            'https://europepmc.org/articles/pmc6172771?pdf=render'

        Args:
            doi (str): The DOI to fetch

        Returns:
            FullTextInfo: Full text information

        """
        # Get metadata
        metadata = self.get_metadata(doi)

        # Check Unpaywall
        unpaywall_data = self.get_unpaywall_info(doi)
        if unpaywall_data and unpaywall_data.get("is_oa"):
            locations = unpaywall_data.get("oa_locations", [])
            if unpaywall_data.get("best_oa_location"):
                best_oa_location = unpaywall_data.get("best_oa_location")
                locations = [best_oa_location] + locations

            # Find best open access location
            for location in locations:
                pdf_url = location.get("url_for_pdf")
                if pdf_url:
                    return FullTextInfo(text=None, pdf_url=pdf_url, source="unpaywall", metadata=metadata)

        # Fallback
        url_prefixes = os.getenv("DOI_FULL_TEXT_URLS", "").split(",")

        for url_prefix in url_prefixes:
            url_prefix.rstrip("/")
            url = f"{url_prefix}/{doi}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    pdf_embed = soup.find("embed", id="pdf")
                    if pdf_embed and pdf_embed.get("src"):
                        pdf_url = pdf_embed["src"]
                        # Remove any URL parameters after #
                        pdf_url = pdf_url.split("#")[0]
                        if not pdf_url.startswith("http"):
                            pdf_url = "https:" + pdf_url
                        return FullTextInfo(
                            pdf_url=pdf_url,
                            source=url,
                            metadata=metadata,
                        )
            except Exception:
                continue

    def text_from_pdf_url(self, pdf_url: str, raise_for_status=False) -> Optional[str]:
        """Extract text from a PDF URL.

        Example:
            >>> fetcher = DOIFetcher()
            >>> pdf_url = "https://ceur-ws.org/Vol-1747/IT201_ICBO2016.pdf"
            >>> text = fetcher.text_from_pdf_url(pdf_url)
            >>> assert "biosphere" in text

        Args:
            pdf_url:
            raise_for_status:

        Returns:

        """
        session = requests_cache.CachedSession("pdf_cache")
        # Download the PDF
        response = session.get(pdf_url)
        if raise_for_status:
            response.raise_for_status()
        if response.status_code != 200:
            return None
        with NamedTemporaryFile(delete=False) as tmpf:
            tmpf.write(response.content)
            tmp_name = tmpf.name
            with open(tmp_name, "wb") as f:
                f.write(response.content)
            md = MarkItDown()
            return md.convert(tmpf.name).text_content

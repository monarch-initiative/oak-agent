import os

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Optional, Dict, Any


class DOIFetcher:
    def __init__(self, email: Optional[str] = None):
        """
        Initialize the DOI fetcher with a contact email (required by some APIs).

        Args:
            email (str): Contact email for API access
        """
        self.email = email or os.getenv('EMAIL')
        if not self.email:
            raise ValueError("Please provide a contact email (EMAIL env var) for API access.")
        self.headers = {
            'User-Agent': f'DOIFetcher/1.0 (mailto:{email})',
            'Accept': 'application/json'
        }

    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and normalized characters."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        return text.strip()

    def get_metadata(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Fetch metadata for a DOI using the Crossref API.

        Args:
            doi (str): The DOI to look up

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary if successful, None otherwise
        """
        base_url = 'https://api.crossref.org/works/'
        try:
            response = requests.get(f'{base_url}{doi}', headers=self.headers)
            response.raise_for_status()
            return response.json()['message']
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return None

    def get_unpaywall_info(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Check Unpaywall for open access versions.

        Args:
            doi (str): The DOI to look up

        Returns:
            Optional[Dict[str, Any]]: Unpaywall data if successful, None otherwise
        """
        base_url = f'https://api.unpaywall.org/v2/{doi}'
        try:
            response = requests.get(f'{base_url}?email={self.email}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error checking Unpaywall: {e}")
            return None

    def get_full_text(self, doi: str) -> Optional[str]:
        info = self.get_full_text_info(doi)
        if not info:
            return None
        text = info.get('text')
        if text:
            return self.clean_text(text)
        metadata = info.get('metadata', {})
        abstract = metadata.get('abstract')
        if abstract:
            return self.clean_text(abstract) + "\n FULL TEXT NOT AVAILABLE"
        return "FULL TEXT NOT AVAILABLE"


    def get_full_text_info(self, doi: str) -> Dict[str, Any]:
        """
        Attempt to get the full text of a paper using various methods.

        Args:
            doi (str): The DOI to fetch

        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'success': bool indicating if full text was found
                - 'text': str of full text if found, otherwise None
                - 'source': str indicating where the text was found
                - 'metadata': dict of metadata if available
                - 'pdf_url': str URL to PDF if available
        """
        result = {
            'success': False,
            'text': None,
            'source': None,
            'metadata': None,
            'pdf_url': None
        }

        # Get metadata
        metadata = self.get_metadata(doi)
        if metadata:
            result['metadata'] = metadata

        # Check Unpaywall
        unpaywall_data = self.get_unpaywall_info(doi)
        if unpaywall_data and unpaywall_data.get('is_oa'):
            best_oa_location = None

            # Find best open access location
            for location in unpaywall_data.get('oa_locations', []):
                if location.get('host_type') == 'publisher':
                    best_oa_location = location
                    break
                elif location.get('version') == 'publishedVersion':
                    best_oa_location = location
                    break
                elif not best_oa_location:
                    best_oa_location = location

            if best_oa_location:
                pdf_url = best_oa_location.get('pdf_url')
                if pdf_url:
                    result['pdf_url'] = pdf_url
                    result['success'] = True
                    result['source'] = 'unpaywall'

        # Try SciHub as a fallback (if legal in your jurisdiction)
        if not result['success']:
            if os.getenv("ENABLE_SCIHUB") == "true":
                scihub_urls = [
                    f'https://sci-hub.se/{doi}',
                    f'https://sci-hub.st/{doi}'
                ]

                for url in scihub_urls:
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            pdf_iframe = soup.find('iframe', id='pdf')
                            if pdf_iframe and pdf_iframe.get('src'):
                                pdf_url = pdf_iframe['src']
                                if not pdf_url.startswith('http'):
                                    pdf_url = 'https:' + pdf_url
                                result['pdf_url'] = pdf_url
                                result['success'] = True
                                result['source'] = 'scihub'
                                break
                    except Exception as e:
                        continue

        return result

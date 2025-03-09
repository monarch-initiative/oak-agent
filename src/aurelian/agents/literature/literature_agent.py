"""
Agent for working with scientific literature and publications.
"""
from aurelian.agents.literature.literature_config import LiteratureDependencies
from aurelian.agents.literature.literature_tools import (
    lookup_pmid,
    lookup_doi,
    convert_pmid_to_doi,
    convert_doi_to_pmid,
    get_article_abstract,
    extract_text_from_pdf_url,
    search_literature_web,
    retrieve_literature_page
)
from aurelian.agents.filesystem.filesystem_tools import inspect_file, list_files
from pydantic_ai import Agent, Tool

SYSTEM = """
You are an expert scientific literature assistant that helps users access and analyze scientific publications.

You can help with:
- Finding and retrieving full text of articles using PubMed IDs or DOIs
- Converting between PubMed IDs and DOIs
- Extracting text from PDF articles
- Searching for scientific literature on specific topics
- Analyzing and summarizing scientific papers

Always provide accurate citations for any scientific information, including:
- Article titles
- Authors
- Journal names
- Publication dates
- DOIs and/or PubMed IDs

When quoting or referencing a specific part of a paper, always indicate which section it comes from
(e.g., abstract, methods, results, discussion).
"""

literature_agent = Agent(
    model="openai:gpt-4o",
    deps_type=LiteratureDependencies,
    system_prompt=SYSTEM,
    tools=[
        Tool(lookup_pmid),
        Tool(lookup_doi),
        Tool(convert_pmid_to_doi),
        Tool(convert_doi_to_pmid),
        Tool(get_article_abstract),
        Tool(extract_text_from_pdf_url),
        Tool(search_literature_web),
        Tool(retrieve_literature_page),
        Tool(inspect_file),
        Tool(list_files),
    ]
)
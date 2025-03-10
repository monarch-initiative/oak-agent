"""
Tools for the chemistry agent.
"""
import io
import httpx
from functools import lru_cache
from typing import List, Dict, Optional

from oaklib import get_adapter
from pydantic_ai import RunContext, BinaryContent, ModelRetry

from aurelian.agents.chemistry.chemistry_config import ChemistryDependencies, ChemicalStructure
from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.search_utils import web_search, retrieve_web_page


@lru_cache
def get_chebi_adapter():
    """Get the ChEBI adapter from oaklib."""
    return get_adapter(f"sqlite:obo:chebi")


def smiles_to_image(smiles: str) -> bytes:
    """
    Convert a SMILES string to an image.
    
    Args:
        smiles: The SMILES representation of a molecule
        
    Returns:
        bytes: PNG image of the molecular structure
        
    Raises:
        ValueError: If the SMILES string is invalid
    """
    from rdkit import Chem
    from rdkit.Chem import Draw
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError(f"Invalid SMILES: {smiles}")
    img = Draw.MolToImage(mol)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


async def draw_structure_and_interpret(ctx: RunContext[ChemistryDependencies], identifier: str, question: str) -> str:
    """
    Draw a chemical structure and analyze it.

    Args:
        ctx: The run context
        identifier: CHEBI ID (e.g. CHEBI:12345) or a SMILES string
        question: Question about the structure to be answered
        
    Returns:
        str: Analysis of the chemical structure
    """
    print(f"Draw Structure: {identifier}, then: {question}")
    structure = ChemicalStructure.from_anything(identifier)
    image_url = structure.chebi_image_url
    img = None
    
    if image_url:
        image_response = httpx.get(image_url)
        img = BinaryContent(data=image_response.content, media_type='image/png')
    else:
        if structure.smiles:
            img = BinaryContent(data=smiles_to_image(structure.smiles), media_type='image/png')
    
    if not img:
        raise ModelRetry("Could not find image for structure")
        
    from aurelian.agents.chemistry.image_agent import structure_image_agent
    result = await structure_image_agent.run(
        [question, img],
        deps=ctx.deps)
    return result.data


async def chebi_search_terms(ctx: RunContext[ChemistryDependencies], query: str) -> List[Dict]:
    """
    Finds similar ontology terms to the search query in ChEBI.

    Args:
        ctx: The run context 
        query: The search query
        
    Returns:
        List[Dict]: List of matching ChEBI terms
    """
    print(f"ChEBI Term Search: {query}")
    return search_ontology(get_chebi_adapter(), query, limit=ctx.deps.max_search_results)


async def search_web_for_chemistry(query: str) -> str:
    """
    Search the web using a text query.

    Args:
        query: The search query
        
    Returns:
        str: Matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)


async def retrieve_chemistry_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Args:
        url: The URL to fetch
        
    Returns:
        str: The contents of the web page
    """
    print(f"Fetch URL: {url}")
    return retrieve_web_page(url)
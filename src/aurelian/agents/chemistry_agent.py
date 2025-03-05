"""
Agent for working with chemical structures.

Currently this is largely geared around interpreting chemical structures.
"""
import io
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Dict, Union, Optional

import httpx
from oaklib import get_adapter
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, BinaryContent, ModelRetry

from aurelian.utils.async_utils import run_sync
from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.search_utils import web_search



@lru_cache
def get_chebi_adapter():
    return get_adapter(f"sqlite:obo:chebi")

class ChemicalStructure(BaseModel):
    chebi_id: Optional[str] = None
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    name: Optional[str] = None

    @property
    def chebi_local_id(self) -> Optional[str]:
        if self.chebi_id:
            return self.chebi_id.split(":")[1]
        return None

    @property
    def chebi_image_url(self) -> str:
        local_id = self.chebi_local_id
        if local_id:
            return f"https://www.ebi.ac.uk/chebi/displayImage.do?defaultImage=true&imageIndex=0&chebiId={local_id}"
        return ""

    @classmethod
    def from_id(cls, id: str) -> 'ChemicalStructure':
        if ":" in id:
            prefix, local_id = id.split(":")
            if prefix.lower() != "chebi":
                raise ValueError(f"Invalid prefix: {prefix}")
            id = "CHEBI:" + local_id
        else:
            id = "CHEBI:" + id
        return cls(chebi_id=id)

    @classmethod
    def from_anything(cls, id: str) -> 'ChemicalStructure':
        if ":" in id:
            return cls.from_id(id)
        # check if valid smiles
        from rdkit import Chem
        mol = Chem.MolFromSmiles(id)
        if mol:
            return cls(smiles=id)
        raise ValueError(f"Invalid identifier: {id}")


@dataclass
class Dependencies:
    """
    Configuration for the ontology mapper agent.

    We include a default set of ontologies because the initial text embedding index is slow..
    this can easily be changed e.g. in command line
    """
    max_search_results: int = 30

chemistry_agent = Agent(
    model="openai:gpt-4o",
    deps_type=Dependencies,
    result_type=str,
    system_prompt=(
        "You are an expert chemist."
    )
)

structure_image_agent = Agent(model='openai:gpt-4o',
                              system_prompt="""You are an expert chemist, able to interpret
                              chemical structure diagrams and answer questions on them.
                              Use the `draw_structure_and_interpret` to render a CHEBI ID
                              or a SMILES string as an image and then ask a question about it.
                              """)

def smiles_to_image(smiles: str) -> bytes:
    from rdkit import Chem
    from rdkit.Chem import Draw
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError(f"Invalid SMILES: {smiles}")
    img = Draw.MolToImage(mol)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@chemistry_agent.tool
def draw_structure_and_interpret(ctx: RunContext[Dependencies], identifier: str, question: str) -> str:
    """
    Draw a chemical structure and analyze it.

    Args:
        identifier: CHEBI ID (e.g. CHEBI:12345) or a SMILES string
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
    return structure_image_agent.run_sync(
        [question, img],
        deps=ctx.deps).data


@chemistry_agent.tool
def chebi_search_terms(ctx: RunContext[Dependencies], query: str) -> List[Dict]:
    """
    Finds similar ontology terms to the search query.

    For example:

        ```
        search_terms("go", "cycle cycle and related processes")
        ```

    Relevancy ranking is used, with semantic similarity, which means
    queries need only be close in semantic space. E.g. while GO does not
    deal with diseases, this may return relevant pathways or structures:

        ```
        search_terms("go", "terms most relevant to Parkinson disease")
        ```

    Args:

        ontology_id: The ontology ID to search in (e.g. cl, go, uberon)
        query: The search query
    """
    print(f"Term Search: {ontology_id} {query}")
    return search_ontology(get_chebi_adapter(), query, limit=ctx.deps.max_search_results)


@chemistry_agent.tool_plain()
def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@chemistry_agent.tool_plain
def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Returns:
        The contents of the web page.
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    return su.retrieve_web_page(url)


def chat(ontologies: Union[str, List[str]], **kwargs):
    import gradio as gr
    deps = Dependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: chemistry_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Chemistry AI Assistant",
        examples=[

        ]
    )

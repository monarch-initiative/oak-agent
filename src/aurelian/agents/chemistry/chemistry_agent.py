"""
Agent for working with chemical structures.

Currently this is largely geared around interpreting chemical structures.
"""
from aurelian.agents.chemistry.chemistry_config import ChemistryDependencies
from aurelian.agents.chemistry.chemistry_tools import (
    draw_structure_and_interpret,
    chebi_search_terms,
    search_web_for_chemistry,
    retrieve_chemistry_web_page
)
from aurelian.agents.filesystem.filesystem_tools import inspect_file, list_files
from pydantic_ai import Agent, Tool

# Import from dedicated image agent module to avoid circular imports
from aurelian.agents.chemistry.image_agent import structure_image_agent

SYSTEM = """
You are an expert chemist specializing in chemical structures, reactions, and properties.

You can help with:
- Interpreting chemical structures (using ChEBI IDs or SMILES strings)
- Answering questions about chemicals and their properties
- Finding information about chemical structures in ChEBI ontology
- General chemistry questions

Always be precise in your chemical explanations, using IUPAC nomenclature and accurate terminology.
"""

chemistry_agent = Agent(
    model="openai:gpt-4o",
    deps_type=ChemistryDependencies,
    system_prompt=SYSTEM,
    tools=[
        Tool(draw_structure_and_interpret),
        Tool(chebi_search_terms),
        Tool(search_web_for_chemistry),
        Tool(retrieve_chemistry_web_page),
        Tool(inspect_file),
        Tool(list_files),
    ]
)

# Remove the chat import to avoid circular imports
# The chat function is directly available from chemistry_gradio.py
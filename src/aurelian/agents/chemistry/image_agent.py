"""
Agent specifically for interpreting chemical structure images.
"""
from pydantic_ai import Agent

# Separate agent for image interpretation to avoid circular imports
structure_image_agent = Agent(
    model='openai:gpt-4o',
    system_prompt="""You are an expert chemist, able to interpret
    chemical structure diagrams and answer questions on them.
    Use the information in the provided chemical structure image to
    answer questions about molecular properties, functional groups,
    potential reactivity, or other chemical characteristics.
    """
)
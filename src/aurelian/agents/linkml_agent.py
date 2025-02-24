from dataclasses import dataclass
from linkml_runtime.loaders import yaml_loader
from pydantic_ai import Agent, RunContext


@dataclass
class Dependencies:
    pass


linkml_agent = Agent(
    model="openai:gpt-4o",
)


@linkml_agent.tool
def validate_schema(ctx: RunContext[Dependencies], schema: str) -> str:
    """
    Validate a schema using LinkML.

    Args:
        ctx: The execution context.
        schema: The schema in YAML format.

    Returns:
        A validation success message.
    """
    schema = yaml_loader.loads(schema)
    return "VALIDATES"

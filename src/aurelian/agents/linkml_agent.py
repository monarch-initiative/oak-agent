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
    schema = yaml_loader.loads(schema)
    return "VALIDATES"
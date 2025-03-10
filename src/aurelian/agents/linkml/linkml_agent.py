"""
Agent for creating LinkML schemas and example datasets
"""
from typing import List

from aurelian.agents.filesystem.filesystem_tools import download_url_as_markdown, inspect_file
from aurelian.agents.linkml.linkml_config import LinkMLDependencies
from aurelian.agents.linkml.linkml_tools import validate_then_save_schema, validate_data
from aurelian.utils.async_utils import run_sync
from pydantic_ai import Agent, Tool

SYSTEM = """
You are an expert data modeler able to assist in creating LinkML schemas.
Always provide the schema in LinkML YAML, unless asked otherwise.
Before providing the user with a schema, you MUST ALWAYS validate it using the `validate_schema` tool.
If there are mistakes, iterate on the schema until it validates.
If it is too hard, ask the user for further guidance.
If you are asked to make schemas for a file, you can look at files using
the `inspect_file` tool.
Always be transparent and show your working and reasoning. If you validate the schema,
tell the user you did this.
You should assume the user is technically competent, and can interpret both YAML
schema files, and example data files in JSON or YAML.
"""

linkml_agent = Agent(
    model="openai:gpt-4o",
    deps_type=LinkMLDependencies,
    tools=[
        Tool(inspect_file),
        Tool(download_url_as_markdown),
        Tool(validate_then_save_schema),
        Tool(validate_data),
    ],
    system_prompt=SYSTEM
)


def chat(workdir: str, **kwargs):
    import gradio as gr
    deps = LinkMLDependencies()
    deps.workdir.location = workdir

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: linkml_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="LinkML AI Assistant",
        examples=[
            ["Generate a schema for modeling the chemical components of foods"],
            ["Generate a schema for this data: {name: 'joe', age: 22}"],
        ]
    )

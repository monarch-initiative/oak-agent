from dataclasses import dataclass, field
from typing import List

import logfire
from aurelian.utils.async_utils import run_sync
from aurelian.utils.search_utils import web_search
from linkml.generators import JsonSchemaGenerator
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.linkml_model import SchemaDefinition
from linkml.validator import validate
from pydantic_ai import Agent, RunContext, AgentRunError

from aurelian.dependencies.workdir import WorkDir


@dataclass
class Dependencies:
    workdir: WorkDir = field(default_factory=lambda: WorkDir())

    def parse_objects_from_file(self, data_file: str) -> List[dict]:
        """
        Parse objects from a file in the working directory.

        Args:
            data_file:

        Returns:

        """
        from linkml_store.utils.format_utils import load_objects
        path_to_file = self.workdir.get_file_path(data_file)
        if not path_to_file.exists():
            raise AgentRunError(f"Data file {data_file} does not exist")
        return load_objects(path_to_file)



linkml_agent = Agent(
    model="openai:gpt-4o",
    system_prompt="""
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
)


@linkml_agent.system_prompt
def add_checklists(ctx: RunContext[Dependencies]) -> str:
    files_names = ctx.deps.workdir.list_file_names()
    if files_names:
        return f"Local files: {files_names}"
    return "No files currently in the working directory"

@linkml_agent.tool
def validate_schema(ctx: RunContext[Dependencies], schema: str, save_to_file="schema.yaml") -> str:
    """
    Validate a LinkML schema.

    Args:
        ctx:
        schema: schema (as yaml) to validate. Do not truncate, always pass the whole schema.
        save_to_file: optional file name to save the schema to. Defaults to schema.yaml

    Returns:

    """
    print(f"Validating schema: {schema}")
    try:
        schema = yaml_loader.loads(schema, target_class=SchemaDefinition)
        gen = JsonSchemaGenerator(schema)
        gen.serialize()
        if save_to_file and schema:
            ctx.deps.workdir.write_file(save_to_file, schema)
    except Exception as e:
        return f"Schema does not validate: {e}"
    return "VALIDATES"

@linkml_agent.tool
def inspect_file(ctx: RunContext[Dependencies], data_file: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        ctx:
        data_file:

    Returns:

    """
    print(f"Inspecting file: {data_file}")
    return ctx.deps.workdir.read_file(data_file)


@linkml_agent.tool
def list_files(ctx: RunContext[Dependencies]) -> str:
    """
    List files in the working directory.

    Args:
        ctx:

    Returns:

    """
    return "\n".join(ctx.deps.workdir.list_file_names())

@linkml_agent.tool
def write_to_file(ctx: RunContext[Dependencies], data: str, file_name: str) -> str:
    """
    Write data to a file in the working directory.

    Args:
        ctx:
        data:
        file_name:

    Returns:

    """
    print(f"Writing data to file: {file_name}")
    ctx.deps.workdir.write_file(file_name, data)
    return f"Data written to {file_name}"

@linkml_agent.tool
def validate_data(ctx: RunContext[Dependencies], schema: str, data_file: str) -> str:
    """
    Validate data file against a schema.

    This assumes the data file is present in the working directory.
    You can write data to the working directory using the `write_to_file` tool.

    Args:
        ctx:
        schema: the schema (as a YAML string)
        data_file: the name of the data file in the working directory

    Returns:

    """
    logfire.log(f"Validating data file: {data_file} using schema: {schema}")
    print(f"Validating data file: {data_file} using schema: {schema}")
    try:
        schema = yaml_loader.loads(schema, target_class=SchemaDefinition)
    except Exception as e:
        return f"Schema does not validate: {e}"
    try:
        instances = ctx.deps.parse_objects_from_file(data_file)
        for instance in instances:
            print(f"Validating {instance}")
            rpt = validate(instance, schema)
            print(f"Validation report: {rpt}")
            if rpt.results:
                return f"Data does not validate:\n{rpt.results}"
        return f"{len(instances)} instances all validate successfully"
    except Exception as e:
        return f"Data does not validate: {e}"


@linkml_agent.tool_plain()
def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Args:
        query: Text query

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@linkml_agent.tool_plain
def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Args:
        url: URL of the web page

    Returns:
        The contents of the web page.
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    return su.retrieve_web_page(url)


@linkml_agent.tool
def download_web_page(ctx: RunContext[Dependencies], url: str, local_file_name: str) -> str:
    """
    Download contents of a web page.

    Args:
        ctx:
        url: URL of the web page
        local_file_name: Name of the local file to save the

    Returns:
        str: messaage
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    data = su.retrieve_web_page(url)
    ctx.deps.workdir.write_file(local_file_name, data)
    return f"Data written to {local_file_name}"




def chat(workdir: str, **kwargs):
    import gradio as gr
    deps = Dependencies()
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

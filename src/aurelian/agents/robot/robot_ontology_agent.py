"""
Agent for creating ROBOT templates and compiling to ontologies.
"""
from dataclasses import dataclass, field
from typing import List, Dict

from aurelian.agents.filesystem.filesystem_tools import inspect_file, download_url_as_markdown, list_files
from aurelian.agents.robot.robot_config import RobotDependencies
from aurelian.agents.robot.robot_tools import write_and_compile_template, fetch_documentation
from aurelian.utils.async_utils import run_sync
from aurelian.utils.search_utils import web_search
from pydantic_ai import Agent, RunContext, Tool

from aurelian.dependencies.workdir import WorkDir, HasWorkdir

SYSTEM = """
Background:

Your job is to iteratively build an ontology via *robot templates*,
These are tabular data (CSV syntax) with a special header that compiles to OWL.

For example, if the request is for an animals ontology, you could start with a CSV with columns Name, ParentTaxon, Eats, 
with rows filled out with some example animals.

The main tool you will use is `write_and_compile_template` which writes the the template content to
a local file after compiling to OWL. This also takes a list of ontologies to import, which
should also be on the file system.

Sometimes you may need to work with multiple dependent ontologies. For example, if you have a vehicle class
hierarchy in `vehicles.csv` and parts in `parts.csv`, and vehicles depends on parts, you would first iterate
on `parts.csv` (e.g. calling `write_and_compile_template`, with no imports), then write vehicles using
`write_and_compile_template` with `['parts.csv']` as the dependencies/imports.

## Robot template CSV structure:

Robot template files have an additional metadata row below the header row. This is called the "template row". It specifies how each column maps to OWL. Typical values will be "ID" for the unique identifier, LABEL for the name, "SC %" for the parent class. Consult the docs for details. Note that this is always beneath the main header row. This can seem a bit duplicative, but that's OK. An example might be:

identifier,name,parent,synonyms
ID,LABEL,SC %,A oboInOwl:hasExactSynonym
ANIMAL:1,chicken,aves,Gallus gallus|chick

The first row is a normal header with human-friendly columns. The 2nd is the robot template row. After that are the usual data rows.

Here "A oboInOwl:hasExactSynonym" in the template row for "synonyms" indicate this column should be interpreted as an owl annotation using that property. Generally the value for annotations is literals/text.

Another common piece of metadata is definitions. For OBO ontologies, IAO must be used here. For non-OBO ontologies people may want to use skos

Some ontologies may need to use other relationships. For part-of parents, use "'part of' some %" (this means that the class indicated by the ID is part-of some X, where X is the value in the part-of column). Use other relationships as appropriate. If you are unclear about the semantics, then consult the docs. You can also work through the docs with the user.

Note that any terms referenced as parents or in logical axioms such as part-of should be in the ontology, so make sure they have rows in the CSV.  It's OK to use the label. For example:

identifier,primary_name,parent,madeOf
ID,LABEL,SC %,SC 'made of' some %
VON:1,vehicle,,
VON:2.car,vehicle,wheel|chassis
VON:3,wheel,car part,
VON:4,chassis,car part,

If in doubt, use "A <propertyName>" for metadata and "SC '<relationName>' some %" for logical relationships / graph edges.

If your working dir doesn't contain any object or annotation properties you can make them in a seperate
imported ontology, TYPE is useful for determining the OWL type, for example:

```
ID,Label,Type,Definition
ID,LABEL,TYPE,A IAO:0000115
IAO:0000115,definition,owl:AnnotationProperty
BFO:0000050,part_of,owl:ObjectProperty
```

If you need any more detailed documentation, you can fetch it with `fetch_documentation`

You can look at files with `inspect_file`

Use scientific language as far as possible. For IDs, these should be numeric curies unless the user requests otherwise. If the user wants to substitute actual ontology term IDs for these, use lookup_curies_get_lookup_get 
"""




robot_ontology_agent = Agent(
    model="openai:gpt-4o",
    deps_type=RobotDependencies,
    system_prompt=SYSTEM,
    tools=[
        Tool(write_and_compile_template, max_retries=2),
        Tool(fetch_documentation),
        Tool(inspect_file),
        Tool(list_files),
        Tool(download_url_as_markdown),
    ]
)


@robot_ontology_agent.system_prompt
def include_templates_in_prompt(ctx: RunContext[RobotDependencies]) -> str:
    files_names = ctx.deps.workdir.list_file_names()
    s = "Working directory files/templates:"
    if files_names:
        for f in files_names:
            s += f"{f}\n---"
            s += ctx.deps.workdir.read_file(f)
            s += "\n"
    return s


@robot_ontology_agent.system_prompt
def include_prefixes_in_prompt(ctx: RunContext[RobotDependencies]) -> str:
    pmap = ctx.deps.prefix_map
    return f"Prefixes: {pmap}"






def chat(workdir: str, **kwargs):
    import gradio as gr
    deps = RobotDependencies()
    deps.workdir.location = workdir

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: robot_ontology_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="robot AI Assistant",
        examples=[
            ["Create an ontology of snacks"],
        ]
    )

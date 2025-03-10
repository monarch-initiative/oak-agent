import asyncio

import pytest
import os

from pydantic_ai import RunContext

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.linkml.linkml_agent import linkml_agent
from aurelian.agents.filesystem.filesystem_tools import write_to_file
from aurelian.agents.linkml.linkml_config import LinkMLDependencies
from aurelian.dependencies.workdir import WorkDir


@pytest.fixture
def deps() -> LinkMLDependencies:
    dep = LinkMLDependencies()
    dep.workdir = WorkDir.create_temporary_workdir()
    return dep

@pytest.mark.parametrize(
    "query,files,ideal",
    [
        ("Download this https://schema.org/PostalAddress -- make a linkml schema for it, then show it to me",
           [], ("postOfficeBoxNumber",)),
        ("""Create a simple schema for a Person with a name and age.
            Example data: {name: 'joe', age: 22}""", [], ("age", "integer")),
        ("Create a schema for objs.json, and ensure it validates",
         [("objs.json", [{"name": "joe", "age": 22}])],
            ("Person", "age", "integer")),
    ]
)
def test_linkml_agent(record_property, deps, query, files, ideal):
    record_property("agent", str(linkml_agent))
    record_property("query", query)
    if files:
        for (fn, content) in files:
            if not isinstance(content, str):
                from linkml_store.utils.format_utils import render_output, guess_format
                fmt = guess_format(fn)
                content = render_output(content, fmt)
                content = content.strip()
            deps.workdir.write_file(fn, content)
            record_property("file", f"{fn}:\n```json\n{content}\n```")
    r = linkml_agent.run_sync(query, deps=deps)
    data = r.data
    record_property("result", str(data))
    record_property("expected", str(ideal))
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, (list, tuple)):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data


def test_write_to_file(deps):
    ctx = RunContext[LinkMLDependencies](deps=deps, model=None, usage=None, prompt=None)
    r = asyncio.run(write_to_file(ctx, "test.txt", "Hello, world!"))
    print(f"RESULT: {r}")
    assert deps.workdir.read_file("test.txt") == "Hello, world!"
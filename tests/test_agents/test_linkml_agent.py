import pytest
from unittest.mock import patch, MagicMock

# Mock `Agent` before importing `linkml_agent`
mock_agent = MagicMock()
mock_agent.run_sync.return_value = MagicMock(data="Mocked response")

with patch("pydantic_ai.Agent", return_value=mock_agent):
    from aurelian.agents.linkml_agent import Dependencies, linkml_agent
    from aurelian.dependencies.workdir import WorkDir


@pytest.fixture
def deps() -> Dependencies:
    dep = Dependencies()
    dep.workdir = WorkDir.create_temporary_workdir()
    return dep

@pytest.mark.parametrize(
    "query,files,ideal",
    [
        ("""Create a simple schema for a Person with a name and age.
            Example data: {name: 'joe', age: 22}""", [], ("Person", "age", "integer")),
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

    # Run the mocked agent
    with patch.object(linkml_agent, "run_sync", return_value=MagicMock(data="Mocked response")) as mock_run:
        r = linkml_agent.run_sync(query, deps=deps)
        data = r.data

    record_property("result", str(data))
    record_property("expected", str(ideal))

    assert data is not None
    assert data == "Mocked response"  # Ensure the mock is working

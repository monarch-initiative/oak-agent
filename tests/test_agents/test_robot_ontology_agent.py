import pytest
import os

from aurelian.dependencies.workdir import WorkDir

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.robot.robot_ontology_agent import robot_ontology_agent
from aurelian.agents.robot.robot_config import RobotDependencies

IMPORTS_CSV = """ID,Label,Type,Definition
ID,LABEL,TYPE,A IAO:0000115
IAO:0000115,definition,owl:AnnotationProperty
BFO:0000050,part_of,owl:ObjectProperty
SNACK:0000001,has ingredient,owl:ObjectProperty
"""

INGREDIENTS_CSV = """ID,Label,Parent,Definition
ID,LABEL,SC %,A IAO:0000115
SNACK:0000002,ingredient,,a component of food
SNACK:0000003,oil,ingredient,
SNACK:0000004,water,ingredient,
SNACK:0000005,flour,ingredient,
"""

@pytest.fixture
def deps():
    dep = RobotDependencies(prefix_map={"SNACK": "http://example.org/snack#"})
    dep.workdir = WorkDir.create_temporary_workdir()
    dep.workdir.write_file("properties.csv", IMPORTS_CSV)
    dep.import_ontology = "properties.csv"
    return dep

@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Create an ontology of snacks", ""),
    ]
)
def test_robot_ontology_agent(record_property, deps, query, ideal):
    record_property("agent", str(robot_ontology_agent))
    record_property("query", query)
    r = robot_ontology_agent.run_sync(query, deps=deps)
    data = r.data
    record_property("result", str(data))
    assert data is not None
    if ideal is not None:
        assert ideal in data
    print(f"FILES: {deps.workdir.list_file_names()}")
    owl_files = [f for f in deps.workdir.list_file_names() if f.endswith(".owl")]
    assert len(owl_files) > 0
    for f in owl_files:
        owl_data = deps.workdir.read_file(f)
        print(owl_data)
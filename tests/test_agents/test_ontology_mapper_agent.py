import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.ontology_mapper_agent import OntologyMapperDependencies, ontology_mapper_agent


@pytest.fixture
def deps() -> OntologyMapperDependencies:
    return OntologyMapperDependencies()

@pytest.mark.parametrize(
    "query,ideal,ontologies",
    [
        ("Find the term in the cell ontology for neuron", "CL:0000540", None),
#        ("Best terms to use for the middle 3 fingers", ("UBERON:0006050", "UBERON:0006049"), None),
    ]
)
def test_ontology_mapper_agent(record_property, deps, query, ideal, ontologies):
    record_property("agent", str(ontology_mapper_agent))
    record_property("query", query)
    r = ontology_mapper_agent.run_sync(query, deps=deps)
    data = r.data
    record_property("result", str(data))
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, (tuple, set, list)):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data

import os

import pytest

from aurelian.agents.ontology_mapper_agent import OntologyDependencies, ontology_mapper_agent

pytestmark = pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skipping in GitHub Actions"
)
@pytest.fixture
def deps() -> OntologyDependencies:
    return OntologyDependencies()

@pytest.mark.parametrize(
    "query,ideal,ontologies",
    [
        ("Find the term in the cell ontology for neuron", "CL:0000540", None),
#        ("Best terms to use for the middle 3 fingers", ("UBERON:0006050", "UBERON:0006049"), None),
    ]
)
def test_ontology_mapper_agent(deps, query, ideal, ontologies):
    r = ontology_mapper_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, (tuple, set, list)):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data

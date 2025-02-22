import pytest

from aurelian.agents.diagnosis_agent import DiagnosisDependencies, diagnosis_agent


@pytest.fixture
def deps():
    return DiagnosisDependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Find the Mondo ID for Marfan syndrome", "MONDO:0007947"),
    ],
)
def test_ubergraph_agent(deps, query, ideal):
    r = diagnosis_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, list):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data

import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.diagnosis_agent import DiagnosisDependencies, diagnosis_agent


@pytest.fixture
def deps():
    return DiagnosisDependencies()


@pytest.mark.parametrize(
    "query,ideal,model",
    [
        ("Find the Mondo ID for Marfan syndrome", "MONDO:0007947", None),
        (
            """Patient has growth failure, distinct facial features, alopecia, and skin aging.
            Findings excluded: Pigmented nevi, cafe-au-lait spots, and photosensitivity.
            Onset was in infancy.
            Return diagnosis with MONDO ID""",
            "MONDO:0008310",
            "openai:gpt-4o",
        ),
        ("All eye phenotypes for Marfan syndrome (include HPO IDs)", "HP:0000518", None),
    ],
)
def test_ubergraph_agent(deps, query, ideal, model):
    kwargs = {"model": model} if model else {}
    r = diagnosis_agent.run_sync(query, deps=deps, **kwargs)
    data = r.data
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, list):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data

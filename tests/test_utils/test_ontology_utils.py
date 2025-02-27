import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.utils.ontology_utils import search_ontology
from oaklib import get_adapter

@pytest.mark.parametrize("handle,term,limit,expected", [
    ("sqlite:obo:bfo", "3D spatial", 10, [("BFO:0000028", "three-dimensional spatial region")]),
])
def test_search_ontology(record_property, handle, term, limit, expected):
    adapter = get_adapter(handle)
    record_property("query", term)
    results = search_ontology(adapter, term, limit=limit)
    record_property("results", results)
    for e in expected:
        assert e in results


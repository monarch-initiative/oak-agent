"""Tests for the Scientific Knowledge Extraction Agent's knowledge extraction capabilities."""

import os
import pytest
import shutil
import asyncio
from pathlib import Path

from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    list_pdf_files,
    extract_knowledge,
    get_extracted_knowledge
)

# Path to test data
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "pdfs")
TEST_PDF = os.path.join(TEST_DATA_DIR, "Ovod et al. - 2017 - Amyloid β concentrations and stable isotope labeli.pdf")
TEST_CACHE_DIR = os.path.join(TEST_DATA_DIR, ".cache")


class MockContext:
    """Mock run context for testing."""
    
    def __init__(self, deps):
        self.dependencies = deps


@pytest.fixture
def setup_test_env():
    """Set up test environment and clean up afterward."""
    # Ensure cache directory exists and is clean
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)
    os.makedirs(TEST_CACHE_DIR, exist_ok=True)
    
    # Create dependencies and context
    deps = ScientificKnowledgeExtractionDependencies(
        pdf_directory=TEST_DATA_DIR,
        cache_directory=TEST_CACHE_DIR
    )
    ctx = MockContext(deps)
    
    yield ctx
    
    # Clean up
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)


@pytest.mark.asyncio
async def test_list_pdf_files(setup_test_env):
    """Test that PDF files can be listed correctly."""
    ctx = setup_test_env
    
    pdfs = await list_pdf_files(ctx)
    
    assert len(pdfs) >= 1, "Should find at least one PDF file"
    assert any(pdf["filename"] == os.path.basename(TEST_PDF) for pdf in pdfs), "Should find the test PDF file"


@pytest.mark.asyncio
async def test_extract_knowledge(setup_test_env):
    """Test knowledge extraction from the Alzheimer's paper."""
    ctx = setup_test_env
    
    # Extract knowledge from the PDF
    assertions = await extract_knowledge(ctx, TEST_PDF)
    
    # Verify we extracted some assertions
    assert len(assertions) > 0, "Should extract at least one assertion"
    
    # Check structure of assertions
    for assertion in assertions:
        assert "subject" in assertion, "Assertion should have a subject"
        assert "predicate" in assertion, "Assertion should have a predicate"
        assert "object" in assertion, "Assertion should have an object"
        assert "evidence" in assertion, "Assertion should have evidence"
    
    # Check that some assertions are about amyloid
    amyloid_assertions = [a for a in assertions if "amyloid" in a["subject"].lower() or "amyloid" in a["object"].lower()]
    assert len(amyloid_assertions) > 0, "Should extract assertions about amyloid"


@pytest.mark.asyncio
async def test_get_extracted_knowledge(setup_test_env):
    """Test retrieving cached extracted knowledge."""
    ctx = setup_test_env
    
    # First extract knowledge to populate the cache
    await extract_knowledge(ctx, TEST_PDF)
    
    # Now retrieve the cached knowledge
    assertions = await get_extracted_knowledge(ctx)
    
    # Verify we got the cached assertions
    assert len(assertions) > 0, "Should retrieve cached assertions"
    
    # Now get assertions for a specific file
    file_assertions = await get_extracted_knowledge(ctx, TEST_PDF)
    
    # Verify we got the same assertions
    assert len(file_assertions) == len(assertions), "Should retrieve the same number of assertions"


if __name__ == "__main__":
    # For manual testing
    async def run_tests():
        ctx = MockContext(ScientificKnowledgeExtractionDependencies(
            pdf_directory=TEST_DATA_DIR,
            cache_directory=TEST_CACHE_DIR
        ))
        
        print("\n==== PDF Files ====")
        pdfs = await list_pdf_files(ctx)
        print(f"Found {len(pdfs)} PDF files")
        for pdf in pdfs:
            print(f"- {pdf['filename']} (Processed: {pdf['is_processed']})")
        
        print("\n==== Extracting Knowledge ====")
        assertions = await extract_knowledge(ctx, TEST_PDF)
        print(f"Extracted {len(assertions)} assertions")
        
        print("\n==== Assertions ====")
        for i, assertion in enumerate(assertions[:5], 1):  # Show first 5
            print(f"\nAssertion {i}:")
            print(f"Subject: {assertion['subject']}")
            print(f"Predicate: {assertion['predicate']}")
            print(f"Object: {assertion['object']}")
            print(f"Evidence: {assertion['evidence'][:100]}...")  # First 100 chars
    
    asyncio.run(run_tests())
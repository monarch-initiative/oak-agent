"""Tests for the Scientific Knowledge Extraction Agent."""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    list_pdf_files,
    get_pdf_content,
    extract_knowledge,
    get_unprocessed_pdfs,
    process_all_unprocessed_pdfs,
    get_extracted_knowledge
)


class MockRunContext:
    """Mock RunContext for testing."""
    
    def __init__(self, dependencies=None):
        self.dependencies = dependencies


@pytest.fixture
def temp_pdf_dir():
    """Create a temporary directory for PDF files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create some empty PDF files for testing
    for i in range(3):
        pdf_path = os.path.join(temp_dir, f"test{i}.pdf")
        with open(pdf_path, 'w') as f:
            f.write(f"Test PDF {i} content")
    
    yield temp_dir
    
    # Clean up
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for caching."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_dependencies(temp_pdf_dir, temp_cache_dir):
    """Create mock dependencies for testing."""
    deps = ScientificKnowledgeExtractionDependencies(
        pdf_directory=temp_pdf_dir,
        cache_directory=temp_cache_dir
    )
    return deps


@pytest.fixture
def mock_context(mock_dependencies):
    """Create a mock run context with dependencies."""
    return MockRunContext(dependencies=mock_dependencies)


@pytest.mark.asyncio
async def test_list_pdf_files(mock_context):
    """Test listing PDF files."""
    result = await list_pdf_files(mock_context)
    
    assert len(result) == 3
    assert all(item["filename"].endswith(".pdf") for item in result)
    assert all(not item["is_processed"] for item in result)


@pytest.mark.asyncio
async def test_get_unprocessed_pdfs(mock_context):
    """Test getting unprocessed PDFs."""
    result = await get_unprocessed_pdfs(mock_context)
    
    assert len(result) == 3
    assert all(Path(pdf_path).name.endswith(".pdf") for pdf_path in result)


@pytest.mark.asyncio
async def test_caching_mechanism(mock_context):
    """Test that the caching mechanism works."""
    # The issue appears to be that while is_processed() correctly identifies processed files,
    # the get_cached_knowledge() might be returning None, leading to _extract_knowledge_with_llm
    # being called a second time. Let's fix this by ensuring the mock data is properly cached.
    
    # Prepare a test file path
    pdf_path = os.path.join(mock_context.dependencies.pdf_directory, "test0.pdf")
    
    # Pre-populate the cache with dummy knowledge for our test file
    dummy_knowledge = [{"subject": "test", "predicate": "test", "object": "test", "evidence": "test"}]
    mock_context.dependencies.mark_as_processed(pdf_path, dummy_knowledge)
    
    # Verify cache is working properly
    assert mock_context.dependencies.is_processed(pdf_path)
    cached_knowledge = mock_context.dependencies.get_cached_knowledge(pdf_path)
    assert cached_knowledge == dummy_knowledge
    
    # Mock the extraction function to confirm it's not called
    with patch('aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools._extract_knowledge_with_llm') as mock_extract:
        # Process the already cached file
        result = await extract_knowledge(mock_context, pdf_path)
        
        # Verify we got the cached knowledge back
        assert result == dummy_knowledge
        
        # Verify the extraction function was never called
        assert mock_extract.call_count == 0


@pytest.mark.asyncio
async def test_process_all_unprocessed_pdfs(mock_context):
    """Test processing all unprocessed PDFs."""
    # Mock extract_knowledge to avoid actual processing
    with patch('aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools.extract_knowledge') as mock_extract:
        mock_extract.return_value = [{"subject": "test", "predicate": "relates_to", "object": "result"}]
        
        result = await process_all_unprocessed_pdfs(mock_context)
        
        assert result["status"] == "success"
        assert result["processed"] == 3
        assert "total_assertions" in result
        assert len(result["files"]) == 3


@pytest.mark.asyncio
async def test_get_extracted_knowledge(mock_context):
    """Test getting previously extracted knowledge."""
    # Add some mock assertions to the cache
    pdf_path = os.path.join(mock_context.dependencies.pdf_directory, "test0.pdf")
    mock_assertions = [
        {"subject": "substance", "predicate": "inhibits", "object": "enzyme", "evidence": "test"}
    ]
    mock_context.dependencies.mark_as_processed(pdf_path, mock_assertions)
    
    # Get knowledge for specific file
    result = await get_extracted_knowledge(mock_context, pdf_path)
    assert len(result) == 1
    assert result[0]["subject"] == "substance"
    
    # Get all knowledge
    all_result = await get_extracted_knowledge(mock_context)
    assert len(all_result) == 1
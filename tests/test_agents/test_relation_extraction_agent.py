"""Tests for the Relation Extraction Agent."""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from aurelian.agents.relation_extraction.relation_extraction_config import RelationExtractionDependencies
from aurelian.agents.relation_extraction.relation_extraction_tools import (
    list_pdf_files,
    get_pdf_content,
    extract_relations,
    get_unprocessed_pdfs,
    process_all_unprocessed_pdfs,
    get_extracted_relations
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
    deps = RelationExtractionDependencies(
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
    # Mock PDF processing
    with patch('aurelian.agents.relation_extraction.relation_extraction_tools.get_pdf_content') as mock_get_content:
        mock_get_content.return_value = {
            "filename": "test0.pdf",
            "file_path": os.path.join(mock_context.dependencies.pdf_directory, "test0.pdf"),
            "text": "Sample PDF content for testing relation extraction",
            "metadata": {"doi": "10.1234/test"}
        }
        
        # Mock relation extraction
        with patch('aurelian.agents.relation_extraction.relation_extraction_tools._extract_relations_with_llm') as mock_extract:
            mock_extract.return_value = []
            
            # Process a file
            pdf_path = os.path.join(mock_context.dependencies.pdf_directory, "test0.pdf")
            await extract_relations(mock_context, pdf_path)
            
            # Verify it's now marked as processed
            assert mock_context.dependencies.is_processed(pdf_path)
            
            # Process again - should use cache
            await extract_relations(mock_context, pdf_path)
            
            # Verify extract function was only called once
            assert mock_extract.call_count == 1


@pytest.mark.asyncio
async def test_process_all_unprocessed_pdfs(mock_context):
    """Test processing all unprocessed PDFs."""
    # Mock extract_relations to avoid actual processing
    with patch('aurelian.agents.relation_extraction.relation_extraction_tools.extract_relations') as mock_extract:
        mock_extract.return_value = [{"subject": "test", "predicate": "relates_to", "object": "result"}]
        
        result = await process_all_unprocessed_pdfs(mock_context)
        
        assert result["status"] == "success"
        assert result["processed"] == 3
        assert result["total_relations"] == 3
        assert len(result["files"]) == 3


@pytest.mark.asyncio
async def test_get_extracted_relations(mock_context):
    """Test getting previously extracted relations."""
    # Add some mock relations to the cache
    pdf_path = os.path.join(mock_context.dependencies.pdf_directory, "test0.pdf")
    mock_relations = [
        {"subject": "substance", "predicate": "inhibits", "object": "enzyme", "evidence": "test"}
    ]
    mock_context.dependencies.mark_as_processed(pdf_path, mock_relations)
    
    # Get relations for specific file
    result = await get_extracted_relations(mock_context, pdf_path)
    assert len(result) == 1
    assert result[0]["subject"] == "substance"
    
    # Get all relations
    all_result = await get_extracted_relations(mock_context)
    assert len(all_result) == 1
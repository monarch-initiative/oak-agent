"""Tools for the Relation Extraction Agent."""

import os
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
import re
from dataclasses import dataclass

from pydantic_ai import RunContext, ModelRetry

# Import utilities from aurelian
from aurelian.utils.pdf_fetcher import extract_text_from_pdf
from aurelian.utils.pubmed_utils import (
    get_data_from_doi, 
    get_data_from_pmid
)


@dataclass
class Relation:
    """Represents an extracted relation (triple) from a scientific paper."""
    
    # The subject of the relation (entity or concept)
    subject: str
    
    # The predicate/relation type
    predicate: str
    
    # The object of the relation (entity or concept)
    object: str
    
    # Evidence for the relation (e.g., specific sentence from the paper)
    evidence: str
    
    # Confidence score (0-1) of the relation extraction
    confidence: float = 1.0
    
    # Paper metadata
    paper_doi: Optional[str] = None
    paper_title: Optional[str] = None
    paper_authors: Optional[List[str]] = None
    paper_year: Optional[int] = None
    
    # Section where the relation was found (e.g., "Abstract", "Results")
    section: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to a dictionary for serialization."""
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "paper_doi": self.paper_doi,
            "paper_title": self.paper_title,
            "paper_authors": self.paper_authors,
            "paper_year": self.paper_year,
            "section": self.section
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Relation':
        """Create a Relation from a dictionary."""
        return cls(**data)


async def list_pdf_files(ctx: RunContext) -> List[str]:
    """
    List all available PDF files in the configured directory.
    
    Returns:
        A list of PDF file paths available for processing.
    """
    deps = ctx.dependencies
    
    try:
        if not os.path.exists(deps.pdf_directory):
            raise ModelRetry(f"PDF directory '{deps.pdf_directory}' does not exist.")
        
        pdf_files = []
        for filename in os.listdir(deps.pdf_directory):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(deps.pdf_directory, filename)
                is_processed = deps.is_processed(file_path)
                pdf_files.append({
                    "file_path": file_path,
                    "filename": filename,
                    "is_processed": is_processed
                })
        
        return pdf_files
    
    except Exception as e:
        raise ModelRetry(f"Failed to list PDF files: {str(e)}")


async def get_pdf_content(ctx: RunContext, file_path: str) -> Dict:
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Path to the PDF file to extract text from.
        
    Returns:
        A dictionary containing the extracted text and metadata.
    """
    deps = ctx.dependencies
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise ModelRetry(f"PDF file '{file_path}' does not exist.")
        
        # Extract text from PDF
        pdf_text = await asyncio.to_thread(extract_text_from_pdf, file_path)
        
        # Basic metadata extraction
        filename = os.path.basename(file_path)
        doi = await _extract_doi_from_text(pdf_text)
        
        # Get metadata from DOI if available
        metadata = {}
        if doi:
            try:
                doi_data = await get_data_from_doi(doi)
                metadata = {
                    "doi": doi,
                    "title": doi_data.get("title", ""),
                    "authors": doi_data.get("authors", []),
                    "year": doi_data.get("year"),
                    "journal": doi_data.get("journal", "")
                }
            except Exception as e:
                # Failed to get DOI metadata, but we can continue
                metadata = {"doi": doi}
        
        return {
            "filename": filename,
            "file_path": file_path,
            "text": pdf_text,
            "metadata": metadata
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to extract PDF content: {str(e)}")


async def _extract_doi_from_text(text: str) -> Optional[str]:
    """Extract DOI from text content if present."""
    
    # Common DOI patterns
    doi_patterns = [
        r'(?:doi|DOI):\s*([0-9]+\.[0-9]+\/[^\s\]\)]+)',
        r'(?:https?://)?(?:dx\.)?doi\.org/([0-9]+\.[0-9]+\/[^\s\]\)]+)'
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


async def extract_relations(ctx: RunContext, file_path: str) -> List[Dict]:
    """
    Extract relations from a PDF file.
    
    Args:
        file_path: Path to the PDF file to process.
        
    Returns:
        List of extracted relations as dictionaries.
    """
    deps = ctx.dependencies
    
    try:
        # Check if already processed and cached
        cached_relations = deps.get_cached_relations(file_path)
        if cached_relations:
            return cached_relations
        
        # Get PDF content
        pdf_data = await get_pdf_content(ctx, file_path)
        pdf_text = pdf_data["text"]
        metadata = pdf_data["metadata"]
        
        # TODO: In a real implementation, this would use an NLP pipeline,
        # information extraction model, or prompt engineering to extract relations.
        # For now, we'll simulate extraction with a dummy implementation.
        
        # This is just a placeholder - in a real implementation, 
        # you would use a more sophisticated approach for relation extraction
        relations = await _extract_relations_with_llm(ctx, pdf_text, metadata)
        
        # Cache the results
        relation_dicts = [r.to_dict() for r in relations]
        deps.mark_as_processed(file_path, relation_dicts)
        
        return relation_dicts
    
    except Exception as e:
        raise ModelRetry(f"Failed to extract relations: {str(e)}")


async def _extract_relations_with_llm(
    ctx: RunContext, 
    text: str, 
    metadata: Dict
) -> List[Relation]:
    """
    Extract relations using LLM-based extraction.
    
    This is a placeholder implementation that would be replaced with actual
    LLM-based relation extraction in a production system.
    """
    # This is just a stub - in reality, you would:
    # 1. Split the text into manageable chunks
    # 2. Process each chunk to identify potential relations
    # 3. Use a fine-tuned model or prompt engineering to extract structured relations
    
    # Example dummy implementation
    relations = []
    
    # Split into sections (very simplified)
    sections = text.split("\n\n")
    
    for i, section in enumerate(sections[:5]):  # Process just first 5 sections for this example
        # Skip very short sections
        if len(section) < 100:
            continue
            
        # This would be replaced with actual relation extraction
        # For now, we'll just create a dummy relation based on keywords
        
        # Look for sentence patterns that might indicate relations
        sentences = section.split(". ")
        
        for sentence in sentences:
            # Very simplistic pattern matching - would be replaced with real NLP
            if "increases" in sentence or "enhances" in sentence or "promotes" in sentence:
                parts = sentence.split(" increases " if "increases" in sentence else 
                                     " enhances " if "enhances" in sentence else " promotes ")
                
                if len(parts) == 2:
                    relation = Relation(
                        subject=parts[0].strip(),
                        predicate="increases" if "increases" in sentence else 
                                  "enhances" if "enhances" in sentence else "promotes",
                        object=parts[1].strip(),
                        evidence=sentence,
                        confidence=0.7,
                        paper_doi=metadata.get("doi"),
                        paper_title=metadata.get("title"),
                        paper_authors=metadata.get("authors"),
                        paper_year=metadata.get("year"),
                        section=f"Section {i+1}"
                    )
                    relations.append(relation)
            
            elif "decreases" in sentence or "inhibits" in sentence or "reduces" in sentence:
                parts = sentence.split(" decreases " if "decreases" in sentence else 
                                     " inhibits " if "inhibits" in sentence else " reduces ")
                
                if len(parts) == 2:
                    relation = Relation(
                        subject=parts[0].strip(),
                        predicate="decreases" if "decreases" in sentence else 
                                  "inhibits" if "inhibits" in sentence else "reduces",
                        object=parts[1].strip(),
                        evidence=sentence,
                        confidence=0.7,
                        paper_doi=metadata.get("doi"),
                        paper_title=metadata.get("title"),
                        paper_authors=metadata.get("authors"),
                        paper_year=metadata.get("year"),
                        section=f"Section {i+1}"
                    )
                    relations.append(relation)
    
    return relations


async def get_unprocessed_pdfs(ctx: RunContext) -> List[str]:
    """
    Get a list of PDF files that haven't been processed yet.
    
    Returns:
        A list of unprocessed PDF file paths.
    """
    deps = ctx.dependencies
    
    try:
        unprocessed = deps.get_unprocessed_pdfs()
        return unprocessed
    
    except Exception as e:
        raise ModelRetry(f"Failed to get unprocessed PDFs: {str(e)}")


async def process_all_unprocessed_pdfs(ctx: RunContext) -> Dict:
    """
    Process all unprocessed PDF files in the directory and extract relations.
    
    Returns:
        Summary of the processing results.
    """
    deps = ctx.dependencies
    
    try:
        unprocessed_pdfs = deps.get_unprocessed_pdfs()
        
        if not unprocessed_pdfs:
            return {"status": "success", "message": "No unprocessed PDFs found.", "processed": 0}
        
        total_relations = 0
        processed_files = []
        
        for pdf_path in unprocessed_pdfs:
            try:
                relations = await extract_relations(ctx, pdf_path)
                total_relations += len(relations)
                processed_files.append({
                    "file": os.path.basename(pdf_path),
                    "relations_count": len(relations)
                })
            except Exception as e:
                processed_files.append({
                    "file": os.path.basename(pdf_path),
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "processed": len(processed_files),
            "total_relations": total_relations,
            "files": processed_files
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to process PDFs: {str(e)}")


async def get_extracted_relations(ctx: RunContext, file_path: Optional[str] = None) -> List[Dict]:
    """
    Get previously extracted relations from the cache.
    
    Args:
        file_path: Optional path to a specific PDF file. If not provided,
                  returns relations from all processed files.
                  
    Returns:
        List of relations as dictionaries.
    """
    deps = ctx.dependencies
    
    try:
        if file_path:
            # Get relations for a specific file
            relations = deps.get_cached_relations(file_path)
            return relations or []
        else:
            # Get all relations
            all_relations = []
            
            # List all PDFs
            for filename in os.listdir(deps.pdf_directory):
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(deps.pdf_directory, filename)
                    relations = deps.get_cached_relations(file_path)
                    if relations:
                        all_relations.extend(relations)
            
            return all_relations
    
    except Exception as e:
        raise ModelRetry(f"Failed to get extracted relations: {str(e)}")
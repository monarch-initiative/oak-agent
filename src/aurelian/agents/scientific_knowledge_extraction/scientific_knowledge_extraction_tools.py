"""Tools for the Scientific Knowledge Extraction Agent."""

import os
import json
import asyncio
import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
import re
from dataclasses import dataclass

from pydantic_ai import RunContext, ModelRetry

# Import utilities from aurelian
from aurelian.utils.pdf_fetcher import extract_text_from_pdf

# Define common ontology sources
ONTOLOGY_SOURCES = {
    # Relation Ontology for predicates
    "RO": "http://purl.obolibrary.org/obo/ro.owl",
    
    # Gene Ontology for biological processes, cellular components, molecular functions
    "GO": "http://purl.obolibrary.org/obo/go.owl",
    
    # Chemical Entities of Biological Interest
    "CHEBI": "http://purl.obolibrary.org/obo/chebi.owl",
    
    # Disease Ontology
    "DOID": "http://purl.obolibrary.org/obo/doid.owl",
    
    # Human Phenotype Ontology
    "HP": "http://purl.obolibrary.org/obo/hp.owl",
    
    # Cell Ontology
    "CL": "http://purl.obolibrary.org/obo/cl.owl",
    
    # Molecular interactions
    "MI": "http://purl.obolibrary.org/obo/mi.owl",
    
    # Sequence Ontology
    "SO": "http://purl.obolibrary.org/obo/so.owl",
    
    # Protein Ontology
    "PR": "http://purl.obolibrary.org/obo/pr.owl",
    
    # Uberon (anatomical structures)
    "UBERON": "http://purl.obolibrary.org/obo/uberon.owl"
}

# Define common relation types mapped to ontology terms
RELATION_MAPPINGS = {
    # Causal relationships
    "increases": "RO:0002304",  # causally upstream of, positive effect
    "decreases": "RO:0002305",  # causally upstream of, negative effect
    "causes": "RO:0002506",     # causes or contributes to condition
    "prevents": "RO:0002559",   # prevents or alleviates

    # Regulatory relationships
    "activates": "RO:0002213",  # positively regulates
    "inhibits": "RO:0002212",   # negatively regulates
    "regulates": "RO:0002211",  # regulates
    "modulates": "RO:0002578",  # directly regulates

    # Associative relationships
    "associated_with": "RO:0002451",  # has quality or characteristic
    "correlated_with": "RO:0002610",  # correlated with
    
    # Functional relationships
    "has_function": "RO:0000085",   # has function
    "participates_in": "RO:0000056", # participates in
    "part_of": "BFO:0000050",       # part of
    "has_part": "BFO:0000051",      # has part
    
    # Compositional relationships
    "contains": "RO:0001019",     # contains
    "composed_of": "RO:0002180"   # has component
}


@dataclass
class ScientificAssertion:
    """Represents an extracted scientific assertion (triple) from a scientific paper."""
    
    # The subject of the relation (entity or concept)
    subject: str
    
    # The predicate/relation type
    predicate: str
    
    # The object of the relation (entity or concept)
    object: str
    
    # Evidence for the relation (e.g., specific sentence from the paper)
    evidence: str
    
    # Confidence score (0-1) of the extraction
    confidence: float = 1.0
    
    # Paper metadata
    paper_doi: Optional[str] = None
    paper_title: Optional[str] = None
    paper_authors: Optional[List[str]] = None
    paper_year: Optional[int] = None
    paper_pmid: Optional[str] = None
    
    # Section where the relation was found (e.g., "Abstract", "Results")
    section: Optional[str] = None
    
    # Ontology identifiers for subject, predicate, and object
    subject_ontology_id: Optional[str] = None
    subject_ontology_label: Optional[str] = None
    subject_ontology_source: Optional[str] = None
    
    predicate_ontology_id: Optional[str] = None
    predicate_ontology_label: Optional[str] = None
    predicate_ontology_source: Optional[str] = None
    
    object_ontology_id: Optional[str] = None
    object_ontology_label: Optional[str] = None
    object_ontology_source: Optional[str] = None
    
    # Additional provenance information
    extraction_date: Optional[str] = None
    extraction_method: Optional[str] = None
    sentence_location: Optional[int] = None  # Approximate location in document
    
    def to_dict(self) -> Dict:
        """Convert to a dictionary for serialization."""
        return {
            # Core triple
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            
            # Evidence and confidence
            "evidence": self.evidence,
            "confidence": self.confidence,
            
            # Paper metadata
            "paper_doi": self.paper_doi,
            "paper_title": self.paper_title,
            "paper_authors": self.paper_authors,
            "paper_year": self.paper_year,
            "paper_pmid": self.paper_pmid,
            "section": self.section,
            
            # Ontology information
            "subject_ontology_id": self.subject_ontology_id,
            "subject_ontology_label": self.subject_ontology_label,
            "subject_ontology_source": self.subject_ontology_source,
            
            "predicate_ontology_id": self.predicate_ontology_id,
            "predicate_ontology_label": self.predicate_ontology_label,
            "predicate_ontology_source": self.predicate_ontology_source,
            
            "object_ontology_id": self.object_ontology_id,
            "object_ontology_label": self.object_ontology_label,
            "object_ontology_source": self.object_ontology_source,
            
            # Additional provenance
            "extraction_date": self.extraction_date,
            "extraction_method": self.extraction_method,
            "sentence_location": self.sentence_location
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScientificAssertion':
        """Create a ScientificAssertion from a dictionary."""
        return cls(**data)
    
    def to_rdf_triple(self) -> str:
        """Generate an RDF triple representation using ontology IDs if available."""
        # Use ontology IDs if available, otherwise use text labels
        subject_id = self.subject_ontology_id if self.subject_ontology_id else f'"{self.subject}"'
        predicate_id = self.predicate_ontology_id if self.predicate_ontology_id else f'"{self.predicate}"'
        object_id = self.object_ontology_id if self.object_ontology_id else f'"{self.object}"'
        
        return f"{subject_id} {predicate_id} {object_id} ."
    
    def to_nanopub(self) -> Dict:
        """
        Generate a nanopublication format with full provenance.
        
        Nanopublications are a formalized way to publish scientific assertions with 
        provenance and publication information.
        """
        # Basic assertion
        assertion = {
            "subject": self.subject_ontology_id or self.subject,
            "predicate": self.predicate_ontology_id or self.predicate,
            "object": self.object_ontology_id or self.object
        }
        
        # Provenance information
        provenance = {
            "evidence_text": self.evidence,
            "confidence": self.confidence,
            "source_doi": self.paper_doi,
            "extraction_method": self.extraction_method or "scientific_knowledge_extraction_agent"
        }
        
        # Publication information
        publication_info = {
            "paper_title": self.paper_title,
            "paper_authors": self.paper_authors,
            "paper_year": self.paper_year,
            "paper_doi": self.paper_doi,
            "paper_pmid": self.paper_pmid
        }
        
        return {
            "assertion": assertion,
            "provenance": provenance,
            "publication_info": publication_info
        }


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
        
        # Extract text from PDF using pdfminer directly
        from pdfminer.high_level import extract_text
        pdf_text = await asyncio.to_thread(extract_text, file_path)
        
        # Basic metadata extraction
        filename = os.path.basename(file_path)
        doi = await _extract_doi_from_text(pdf_text)
        
        # Basic metadata with just the DOI
        metadata = {}
        if doi:
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


async def extract_knowledge(ctx: RunContext, file_path: str) -> List[Dict]:
    """
    Extract scientific knowledge from a PDF file.
    
    Args:
        file_path: Path to the PDF file to process.
        
    Returns:
        List of extracted scientific assertions as dictionaries.
    """
    deps = ctx.dependencies
    
    try:
        # Check if already processed and cached
        cached_knowledge = deps.get_cached_knowledge(file_path)
        if cached_knowledge:
            return cached_knowledge
        
        # Get PDF content
        pdf_data = await get_pdf_content(ctx, file_path)
        pdf_text = pdf_data["text"]
        metadata = pdf_data["metadata"]
        
        # TODO: In a real implementation, this would use an NLP pipeline,
        # information extraction model, or prompt engineering to extract knowledge.
        # For now, we'll simulate extraction with a placeholder implementation.
        
        knowledge = await _extract_knowledge_with_llm(ctx, pdf_text, metadata)
        
        # Cache the results
        knowledge_dicts = [k.to_dict() for k in knowledge]
        deps.mark_as_processed(file_path, knowledge_dicts)
        
        return knowledge_dicts
    
    except Exception as e:
        raise ModelRetry(f"Failed to extract knowledge: {str(e)}")


async def _extract_knowledge_with_llm(
    ctx: RunContext, 
    text: str, 
    metadata: Dict
) -> List[ScientificAssertion]:
    """
    Extract scientific knowledge using LLM-based extraction.
    
    This is a placeholder implementation that would be replaced with actual
    LLM-based knowledge extraction in a production system.
    """
    # This is just a stub - in reality, you would:
    # 1. Split the text into manageable chunks
    # 2. Process each chunk to identify potential assertions
    # 3. Use a fine-tuned model or prompt engineering to extract structured knowledge
    
    # Example dummy implementation
    assertions = []
    
    # Split into sections (very simplified)
    sections = text.split("\n\n")
    
    for i, section in enumerate(sections[:5]):  # Process just first 5 sections for this example
        # Skip very short sections
        if len(section) < 100:
            continue
            
        # This would be replaced with actual knowledge extraction
        # For now, we'll just create a dummy relation based on keywords
        
        # Look for sentence patterns that might indicate relations
        sentences = section.split(". ")
        
        for sentence in sentences:
            # Very simplistic pattern matching for Alzheimer's paper
            # Look for sentences about amyloid beta or related terms
            lower_sentence = sentence.lower()
            if "amyloid" in lower_sentence or "aβ" in lower_sentence or "alzheimer" in lower_sentence:
                # Create an assertion about amyloid beta
                if len(sentence) > 20:  # Only use meaningful sentences
                    # Try to identify subject and object
                    if ":" in sentence or "," in sentence:
                        parts = sentence.split(":" if ":" in sentence else ",", 1)
                        subject = parts[0].strip()
                        object_part = parts[1].strip()
                    else:
                        # Default if we can't split nicely
                        subject = "Amyloid beta"
                        object_part = sentence
                        
                    assertion = ScientificAssertion(
                        subject=subject[:100],  # Limit length
                        predicate="associated_with",
                        object=object_part[:100],  # Limit length
                        evidence=sentence,
                        confidence=0.6,
                        paper_doi=metadata.get("doi"),
                        paper_title="Amyloid β concentrations and stable isotope labeling",
                        paper_authors=["Ovod et al."],
                        paper_year=2017,
                        section=f"Section {i+1}"
                    )
                    assertions.append(assertion)
    
    return assertions


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
    Process all unprocessed PDF files in the directory and extract knowledge.
    
    Returns:
        Summary of the processing results.
    """
    deps = ctx.dependencies
    
    try:
        unprocessed_pdfs = deps.get_unprocessed_pdfs()
        
        if not unprocessed_pdfs:
            return {"status": "success", "message": "No unprocessed PDFs found.", "processed": 0}
        
        total_assertions = 0
        processed_files = []
        
        for pdf_path in unprocessed_pdfs:
            try:
                assertions = await extract_knowledge(ctx, pdf_path)
                total_assertions += len(assertions)
                processed_files.append({
                    "file": os.path.basename(pdf_path),
                    "assertions_count": len(assertions)
                })
            except Exception as e:
                processed_files.append({
                    "file": os.path.basename(pdf_path),
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "processed": len(processed_files),
            "total_assertions": total_assertions,
            "files": processed_files
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to process PDFs: {str(e)}")


async def map_assertion_to_ontology(
    ctx: RunContext,
    assertion: Dict,
    ontology_sources: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Map a scientific assertion's subject, predicate, and object to ontology terms.
    
    Args:
        assertion: The assertion dictionary to map
        ontology_sources: Optional dictionary of ontology sources to use for mapping
                        (overrides default ONTOLOGY_SOURCES)
    
    Returns:
        Updated assertion with ontology mappings
    """
    try:
        # Create a copy of the assertion to avoid modifying the original
        mapped_assertion = assertion.copy()
        
        # Use default ontology sources if none provided
        sources = ontology_sources or ONTOLOGY_SOURCES
        
        # 1. Map the predicate (relation type) first - this is easier as we have a fixed set
        predicate = assertion.get("predicate", "").lower()
        predicate_mapping = None
        
        # Check for direct mapping in our predefined mappings
        for key, ontology_id in RELATION_MAPPINGS.items():
            if predicate == key or key in predicate:
                predicate_mapping = {
                    "id": ontology_id,
                    "label": key,
                    "source": "RO"  # Relation Ontology
                }
                break
        
        # If no mapping found with current implementation, we just use the direct mappings
        # This can be enhanced later with actual ontology search
        
        # Update assertion with predicate mapping if found
        if predicate_mapping:
            mapped_assertion["predicate_ontology_id"] = predicate_mapping["id"]
            mapped_assertion["predicate_ontology_label"] = predicate_mapping["label"]
            mapped_assertion["predicate_ontology_source"] = predicate_mapping["source"]
        
        # For subject and object, in this simple implementation, we don't do ontology mapping
        # This can be enhanced later with actual ontology search
        
        # Add provenance for the mapping
        if not mapped_assertion.get("extraction_date"):
            mapped_assertion["extraction_date"] = datetime.datetime.now().isoformat()
        
        if not mapped_assertion.get("extraction_method"):
            mapped_assertion["extraction_method"] = "scientific_knowledge_extraction_agent"
        
        return mapped_assertion
    
    except Exception as e:
        # If mapping fails, return the original assertion with an error note
        assertion["ontology_mapping_error"] = str(e)
        return assertion


# Placeholder for future implementation of ontology matching
async def _find_best_ontology_match(term: str, ontology_sources: Dict[str, str]) -> Optional[Dict]:
    """
    Find the best ontology match for a given term across multiple ontologies.
    
    This is a placeholder function that will be implemented in the future.
    
    Args:
        term: The term to search for
        ontology_sources: Dictionary of ontology sources to search
    
    Returns:
        Best matching ontology term info or None if no match found
    """
    # In the future, this will search ontologies for matching terms
    return None


async def map_all_assertions_to_ontology(ctx: RunContext) -> Dict:
    """
    Map all extracted scientific assertions to ontology terms.
    
    Returns:
        Summary of the mapping process.
    """
    deps = ctx.dependencies
    
    try:
        # Get all extracted assertions
        all_assertions = await get_extracted_knowledge(ctx)
        
        if not all_assertions:
            return {"status": "success", "message": "No assertions found to map.", "mapped": 0}
        
        mapped_count = 0
        unmapped_count = 0
        updated_assertions = []
        
        # Map each assertion to ontology terms
        for assertion in all_assertions:
            mapped_assertion = await map_assertion_to_ontology(ctx, assertion)
            
            # Check if mapping was successful
            has_subject_mapping = "subject_ontology_id" in mapped_assertion and mapped_assertion["subject_ontology_id"]
            has_predicate_mapping = "predicate_ontology_id" in mapped_assertion and mapped_assertion["predicate_ontology_id"]
            has_object_mapping = "object_ontology_id" in mapped_assertion and mapped_assertion["object_ontology_id"]
            
            if has_subject_mapping or has_predicate_mapping or has_object_mapping:
                mapped_count += 1
            else:
                unmapped_count += 1
            
            updated_assertions.append(mapped_assertion)
        
        # Update the cache with the mapped assertions
        # Group assertions by file
        assertions_by_file = {}
        
        # Get file path for each assertion from the cache
        for filename in os.listdir(deps.pdf_directory):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(deps.pdf_directory, filename)
                cached_assertions = deps.get_cached_knowledge(file_path)
                
                if cached_assertions:
                    # Extract DOIs from assertions
                    file_dois = set()
                    for assertion in cached_assertions:
                        if assertion.get("paper_doi"):
                            file_dois.add(assertion["paper_doi"])
                    
                    # Match assertions to files by DOI
                    file_assertions = []
                    for assertion in updated_assertions:
                        if assertion.get("paper_doi") in file_dois:
                            file_assertions.append(assertion)
                    
                    if file_assertions:
                        assertions_by_file[file_path] = file_assertions
        
        # Update the cache for each file
        for file_path, assertions in assertions_by_file.items():
            deps.mark_as_processed(file_path, assertions)
        
        return {
            "status": "success",
            "total": len(all_assertions),
            "mapped": mapped_count,
            "unmapped": unmapped_count,
            "mapping_rate": f"{mapped_count/len(all_assertions)*100:.1f}%" if all_assertions else "0%"
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to map assertions to ontology: {str(e)}")


async def export_assertions_as_rdf(ctx: RunContext, output_path: str) -> Dict:
    """
    Export scientific assertions as RDF triples.
    
    Args:
        output_path: Path to save the RDF file
        
    Returns:
        Information about the export process
    """
    try:
        # Get all assertions
        assertions = await get_extracted_knowledge(ctx)
        
        if not assertions:
            return {"status": "error", "message": "No assertions found to export."}
        
        # Convert assertions to ScientificAssertion objects
        assertion_objects = [ScientificAssertion.from_dict(a) for a in assertions]
        
        # Generate RDF content
        rdf_lines = []
        
        # Add prefixes
        rdf_lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
        rdf_lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
        rdf_lines.append("@prefix obo: <http://purl.obolibrary.org/obo/> .")
        rdf_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
        rdf_lines.append("@prefix prov: <http://www.w3.org/ns/prov#> .")
        rdf_lines.append("@prefix dcterms: <http://purl.org/dc/terms/> .")
        rdf_lines.append("")
        
        # Add each assertion as an RDF triple with provenance
        for i, assertion in enumerate(assertion_objects):
            # Skip assertions with no ontology mappings
            if not (assertion.subject_ontology_id or assertion.predicate_ontology_id or assertion.object_ontology_id):
                continue
                
            # Create a unique identifier for this assertion
            assertion_id = f"_:assertion{i}"
            
            # Add the core triple
            rdf_lines.append(f"{assertion_id} a rdf:Statement ;")
            
            # Use ontology ID if available, otherwise use text value
            if assertion.subject_ontology_id:
                if ":" in assertion.subject_ontology_id:
                    prefix, id_part = assertion.subject_ontology_id.split(":", 1)
                    rdf_lines.append(f"    rdf:subject obo:{prefix}_{id_part} ;")
                else:
                    rdf_lines.append(f"    rdf:subject <{assertion.subject_ontology_id}> ;")
            else:
                rdf_lines.append(f'    rdf:subject "{assertion.subject}"^^xsd:string ;')
            
            if assertion.predicate_ontology_id:
                if ":" in assertion.predicate_ontology_id:
                    prefix, id_part = assertion.predicate_ontology_id.split(":", 1)
                    rdf_lines.append(f"    rdf:predicate obo:{prefix}_{id_part} ;")
                else:
                    rdf_lines.append(f"    rdf:predicate <{assertion.predicate_ontology_id}> ;")
            else:
                rdf_lines.append(f'    rdf:predicate "{assertion.predicate}"^^xsd:string ;')
            
            if assertion.object_ontology_id:
                if ":" in assertion.object_ontology_id:
                    prefix, id_part = assertion.object_ontology_id.split(":", 1)
                    rdf_lines.append(f"    rdf:object obo:{prefix}_{id_part} ;")
                else:
                    rdf_lines.append(f"    rdf:object <{assertion.object_ontology_id}> ;")
            else:
                rdf_lines.append(f'    rdf:object "{assertion.object}"^^xsd:string ;')
            
            # Add provenance information
            rdf_lines.append(f'    prov:wasQuotedFrom <https://doi.org/{assertion.paper_doi}> ;') if assertion.paper_doi else None
            rdf_lines.append(f'    prov:wasGeneratedBy "scientific_knowledge_extraction_agent" ;')
            rdf_lines.append(f'    dcterms:confidence "{assertion.confidence}" ;')
            rdf_lines.append(f'    prov:wasInfluencedBy """') 
            rdf_lines.append(f'{assertion.evidence}')
            rdf_lines.append(f'    """ .')
            rdf_lines.append("")
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write("\n".join(rdf_lines))
        
        return {
            "status": "success",
            "file_path": output_path,
            "triples_count": len([a for a in assertion_objects if a.subject_ontology_id or a.predicate_ontology_id or a.object_ontology_id]),
            "total_assertions": len(assertion_objects)
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to export assertions as RDF: {str(e)}")


async def get_extracted_knowledge(ctx: RunContext, file_path: Optional[str] = None) -> List[Dict]:
    """
    Get previously extracted scientific knowledge from the cache.
    
    Args:
        file_path: Optional path to a specific PDF file. If not provided,
                  returns knowledge from all processed files.
                  
    Returns:
        List of scientific assertions as dictionaries.
    """
    deps = ctx.dependencies
    
    try:
        if file_path:
            # Get knowledge for a specific file
            knowledge = deps.get_cached_knowledge(file_path)
            return knowledge or []
        else:
            # Get all knowledge
            all_knowledge = []
            
            # List all PDFs
            for filename in os.listdir(deps.pdf_directory):
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(deps.pdf_directory, filename)
                    knowledge = deps.get_cached_knowledge(file_path)
                    if knowledge:
                        all_knowledge.extend(knowledge)
            
            return all_knowledge
    
    except Exception as e:
        raise ModelRetry(f"Failed to get extracted knowledge: {str(e)}")
"""Tools for the Relation Extraction Agent."""

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
from aurelian.utils.pubmed_utils import (
    get_data_from_doi, 
    get_data_from_pmid
)
from aurelian.utils.ontology_utils import (
    search_ontology_term,
    get_ontology_ancestors,
    get_ontology_term_by_id
)

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
    def from_dict(cls, data: Dict) -> 'Relation':
        """Create a Relation from a dictionary."""
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
            "extraction_method": self.extraction_method or "relation_extraction_agent"
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


async def map_relation_to_ontology(
    ctx: RunContext,
    relation: Dict,
    ontology_sources: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Map a relation's subject, predicate, and object to ontology terms.
    
    Args:
        relation: The relation dictionary to map
        ontology_sources: Optional dictionary of ontology sources to use for mapping
                        (overrides default ONTOLOGY_SOURCES)
    
    Returns:
        Updated relation with ontology mappings
    """
    try:
        # Create a copy of the relation to avoid modifying the original
        mapped_relation = relation.copy()
        
        # Use default ontology sources if none provided
        sources = ontology_sources or ONTOLOGY_SOURCES
        
        # 1. Map the predicate (relation type) first - this is easier as we have a fixed set
        predicate = relation.get("predicate", "").lower()
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
        
        # If no mapping found, try search
        if not predicate_mapping:
            search_results = await search_ontology_term(predicate, ontology=sources.get("RO"))
            if search_results and len(search_results) > 0:
                best_match = search_results[0]
                predicate_mapping = {
                    "id": best_match.get("id"),
                    "label": best_match.get("label"),
                    "source": "RO"
                }
        
        # Update relation with predicate mapping if found
        if predicate_mapping:
            mapped_relation["predicate_ontology_id"] = predicate_mapping["id"]
            mapped_relation["predicate_ontology_label"] = predicate_mapping["label"]
            mapped_relation["predicate_ontology_source"] = predicate_mapping["source"]
        
        # 2. Map the subject - more complex as it could be from various ontologies
        subject = relation.get("subject", "")
        subject_mapping = await _find_best_ontology_match(subject, sources)
        
        if subject_mapping:
            mapped_relation["subject_ontology_id"] = subject_mapping["id"]
            mapped_relation["subject_ontology_label"] = subject_mapping["label"]
            mapped_relation["subject_ontology_source"] = subject_mapping["source"]
        
        # 3. Map the object
        obj = relation.get("object", "")
        object_mapping = await _find_best_ontology_match(obj, sources)
        
        if object_mapping:
            mapped_relation["object_ontology_id"] = object_mapping["id"]
            mapped_relation["object_ontology_label"] = object_mapping["label"]
            mapped_relation["object_ontology_source"] = object_mapping["source"]
        
        # Add provenance for the mapping
        if not mapped_relation.get("extraction_date"):
            mapped_relation["extraction_date"] = datetime.datetime.now().isoformat()
        
        if not mapped_relation.get("extraction_method"):
            mapped_relation["extraction_method"] = "relation_extraction_agent"
        
        return mapped_relation
    
    except Exception as e:
        # If mapping fails, return the original relation with an error note
        relation["ontology_mapping_error"] = str(e)
        return relation


async def _find_best_ontology_match(term: str, ontology_sources: Dict[str, str]) -> Optional[Dict]:
    """
    Find the best ontology match for a given term across multiple ontologies.
    
    Args:
        term: The term to search for
        ontology_sources: Dictionary of ontology sources to search
    
    Returns:
        Best matching ontology term info or None if no match found
    """
    # Get candidate matches from different ontologies
    candidates = []
    
    # For biological entities, try these ontologies first
    priority_ontologies = ["GO", "CHEBI", "DOID", "PR", "UBERON", "CL"]
    
    # Search priority ontologies first
    for ontology_prefix in priority_ontologies:
        ontology_url = ontology_sources.get(ontology_prefix)
        if not ontology_url:
            continue
            
        try:
            results = await search_ontology_term(term, ontology=ontology_url, max_results=3)
            if results:
                for result in results:
                    candidates.append({
                        "id": result.get("id"),
                        "label": result.get("label"),
                        "source": ontology_prefix,
                        "score": result.get("score", 0),
                        "definition": result.get("definition", "")
                    })
        except Exception:
            # If search fails for an ontology, continue with others
            pass
    
    # Try other ontologies if no good matches found
    if not candidates or all(c.get("score", 0) < 0.7 for c in candidates):
        for ontology_prefix, ontology_url in ontology_sources.items():
            if ontology_prefix in priority_ontologies:
                continue  # Skip already searched ontologies
                
            try:
                results = await search_ontology_term(term, ontology=ontology_url, max_results=2)
                if results:
                    for result in results:
                        candidates.append({
                            "id": result.get("id"),
                            "label": result.get("label"),
                            "source": ontology_prefix,
                            "score": result.get("score", 0),
                            "definition": result.get("definition", "")
                        })
            except Exception:
                # If search fails for an ontology, continue with others
                pass
    
    # Sort candidates by score
    if candidates:
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return candidates[0]
    
    return None


async def map_all_relations_to_ontology(ctx: RunContext) -> Dict:
    """
    Map all extracted relations to ontology terms.
    
    Returns:
        Summary of the mapping process.
    """
    deps = ctx.dependencies
    
    try:
        # Get all extracted relations
        all_relations = await get_extracted_relations(ctx)
        
        if not all_relations:
            return {"status": "success", "message": "No relations found to map.", "mapped": 0}
        
        mapped_count = 0
        unmapped_count = 0
        updated_relations = []
        
        # Map each relation to ontology terms
        for relation in all_relations:
            mapped_relation = await map_relation_to_ontology(ctx, relation)
            
            # Check if mapping was successful
            has_subject_mapping = "subject_ontology_id" in mapped_relation and mapped_relation["subject_ontology_id"]
            has_predicate_mapping = "predicate_ontology_id" in mapped_relation and mapped_relation["predicate_ontology_id"]
            has_object_mapping = "object_ontology_id" in mapped_relation and mapped_relation["object_ontology_id"]
            
            if has_subject_mapping or has_predicate_mapping or has_object_mapping:
                mapped_count += 1
            else:
                unmapped_count += 1
            
            updated_relations.append(mapped_relation)
        
        # Update the cache with the mapped relations
        # Group relations by file
        relations_by_file = {}
        
        # Get file path for each relation from the cache
        for filename in os.listdir(deps.pdf_directory):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(deps.pdf_directory, filename)
                cached_relations = deps.get_cached_relations(file_path)
                
                if cached_relations:
                    # Extract DOIs from relations
                    file_dois = set()
                    for rel in cached_relations:
                        if rel.get("paper_doi"):
                            file_dois.add(rel["paper_doi"])
                    
                    # Match relations to files by DOI
                    file_relations = []
                    for rel in updated_relations:
                        if rel.get("paper_doi") in file_dois:
                            file_relations.append(rel)
                    
                    if file_relations:
                        relations_by_file[file_path] = file_relations
        
        # Update the cache for each file
        for file_path, relations in relations_by_file.items():
            deps.mark_as_processed(file_path, relations)
        
        return {
            "status": "success",
            "total": len(all_relations),
            "mapped": mapped_count,
            "unmapped": unmapped_count,
            "mapping_rate": f"{mapped_count/len(all_relations)*100:.1f}%" if all_relations else "0%"
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to map relations to ontology: {str(e)}")


async def export_relations_as_rdf(ctx: RunContext, output_path: str) -> Dict:
    """
    Export relations as RDF triples.
    
    Args:
        output_path: Path to save the RDF file
        
    Returns:
        Information about the export process
    """
    try:
        # Get all relations
        relations = await get_extracted_relations(ctx)
        
        if not relations:
            return {"status": "error", "message": "No relations found to export."}
        
        # Convert relations to Relation objects
        relation_objects = [Relation.from_dict(r) for r in relations]
        
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
        
        # Add each relation as an RDF triple with provenance
        for i, rel in enumerate(relation_objects):
            # Skip relations with no ontology mappings
            if not (rel.subject_ontology_id or rel.predicate_ontology_id or rel.object_ontology_id):
                continue
                
            # Create a unique identifier for this assertion
            assertion_id = f"_:assertion{i}"
            
            # Add the core triple
            rdf_lines.append(f"{assertion_id} a rdf:Statement ;")
            
            # Use ontology ID if available, otherwise use text value
            if rel.subject_ontology_id:
                if ":" in rel.subject_ontology_id:
                    prefix, id_part = rel.subject_ontology_id.split(":", 1)
                    rdf_lines.append(f"    rdf:subject obo:{prefix}_{id_part} ;")
                else:
                    rdf_lines.append(f"    rdf:subject <{rel.subject_ontology_id}> ;")
            else:
                rdf_lines.append(f'    rdf:subject "{rel.subject}"^^xsd:string ;')
            
            if rel.predicate_ontology_id:
                if ":" in rel.predicate_ontology_id:
                    prefix, id_part = rel.predicate_ontology_id.split(":", 1)
                    rdf_lines.append(f"    rdf:predicate obo:{prefix}_{id_part} ;")
                else:
                    rdf_lines.append(f"    rdf:predicate <{rel.predicate_ontology_id}> ;")
            else:
                rdf_lines.append(f'    rdf:predicate "{rel.predicate}"^^xsd:string ;')
            
            if rel.object_ontology_id:
                if ":" in rel.object_ontology_id:
                    prefix, id_part = rel.object_ontology_id.split(":", 1)
                    rdf_lines.append(f"    rdf:object obo:{prefix}_{id_part} ;")
                else:
                    rdf_lines.append(f"    rdf:object <{rel.object_ontology_id}> ;")
            else:
                rdf_lines.append(f'    rdf:object "{rel.object}"^^xsd:string ;')
            
            # Add provenance information
            rdf_lines.append(f'    prov:wasQuotedFrom <https://doi.org/{rel.paper_doi}> ;') if rel.paper_doi else None
            rdf_lines.append(f'    prov:wasGeneratedBy "relation_extraction_agent" ;')
            rdf_lines.append(f'    dcterms:confidence "{rel.confidence}" ;')
            rdf_lines.append(f'    prov:wasInfluencedBy """') 
            rdf_lines.append(f'{rel.evidence}')
            rdf_lines.append(f'    """ .')
            rdf_lines.append("")
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write("\n".join(rdf_lines))
        
        return {
            "status": "success",
            "file_path": output_path,
            "triples_count": len([r for r in relation_objects if r.subject_ontology_id or r.predicate_ontology_id or r.object_ontology_id]),
            "total_relations": len(relation_objects)
        }
    
    except Exception as e:
        raise ModelRetry(f"Failed to export relations as RDF: {str(e)}")


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
"""
Tools for the AmiGO agent.
"""
from typing import List, Dict

from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.amigo.amigo_config import AmiGODependencies, normalize_pmid
from aurelian.agents.uniprot.uniprot_tools import normalize_uniprot_id
from aurelian.utils.data_utils import obj_to_dict

from oaklib.datamodels.association import Association, NegatedAssociation
from oaklib.implementations.amigo.amigo_implementation import (
    DEFAULT_SELECT_FIELDS, QUALIFIER, BIOENTITY,
    BIOENTITY_LABEL, map_predicate, ANNOTATION_CLASS, ANNOTATION_CLASS_LABEL, 
    REFERENCE, EVIDENCE_TYPE, ASSIGNED_BY,
    _query as amigo_query,
    _normalize
)


async def find_gene_associations(ctx: RunContext[AmiGODependencies], gene_id: str) -> List[Dict]:
    """
    Find gene associations for a given gene or gene product.
    
    Args:
        ctx: The run context
        gene_id: Gene or gene product IDs
        
    Returns:
        List[Dict]: List of gene associations
    """
    print(f"FIND GENE ASSOCIATIONS: {gene_id}")
    try:
        adapter = ctx.deps.get_amigo_adapter()
        normalized_gene_id = ctx.deps.get_gene_id(gene_id)
        assocs = [obj_to_dict(a) for a in adapter.associations([normalized_gene_id])]
        
        if not assocs:
            raise ModelRetry(f"No gene associations found for {gene_id}. Try a different gene identifier.")
            
        return assocs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error finding gene associations for {gene_id}: {str(e)}")


async def find_gene_associations_for_pmid(ctx: RunContext[AmiGODependencies], pmid: str) -> List[Dict]:
    """
    Find gene associations for a given PubMed ID.
    
    Args:
        ctx: The run context
        pmid: The PubMed ID
        
    Returns:
        List[Dict]: List of gene associations for the PubMed ID
    """
    print(f"FIND GENE ASSOCIATIONS FOR PMID: {pmid}")
    try:
        normalized_pmid = normalize_pmid(pmid)
        amigo = ctx.deps.get_amigo_adapter()
        
        print(f"Lookup amigo annotations to PMID: {normalized_pmid}")
        solr = amigo._solr
        select_fields = DEFAULT_SELECT_FIELDS
        results = amigo_query(solr, {"reference": normalized_pmid}, select_fields)
        
        assocs = []
        for doc in results:
            cls = Association
            quals = set(doc.get(QUALIFIER, []))
            if "not" in quals:
                cls = NegatedAssociation
            assoc = cls(
                subject=_normalize(doc[BIOENTITY]),
                subject_label=doc[BIOENTITY_LABEL],
                predicate=map_predicate(quals),
                negated=cls == NegatedAssociation,
                object=doc[ANNOTATION_CLASS],
                object_label=doc[ANNOTATION_CLASS_LABEL],
                publications=doc[REFERENCE],
                evidence_type=doc.get(EVIDENCE_TYPE),
                primary_knowledge_source=doc[ASSIGNED_BY],
                aggregator_knowledge_source="infores:go",
            )
            assocs.append(obj_to_dict(assoc))
            
        if not assocs:
            raise ModelRetry(f"No gene associations found for PMID {pmid}. Try a different PubMed ID.")
            
        return assocs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error finding gene associations for PMID {pmid}: {str(e)}")


async def lookup_uniprot_entry(ctx: RunContext[AmiGODependencies], uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number.
    
    Args:
        ctx: The run context
        uniprot_acc: The Uniprot accession
        
    Returns:
        str: The Uniprot entry text
    """
    print(f"LOOKUP UNIPROT: {uniprot_acc}")
    try:
        normalized_acc = normalize_uniprot_id(uniprot_acc)
        uniprot_service = ctx.deps.get_uniprot_service()
        result = uniprot_service.retrieve(normalized_acc, frmt="txt")
        
        if not result or "Error" in result or "Entry not found" in result:
            raise ModelRetry(f"Could not find UniProt entry for {uniprot_acc}. The accession may be incorrect.")
            
        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving UniProt entry for {uniprot_acc}: {str(e)}")


async def uniprot_mapping(ctx: RunContext[AmiGODependencies], target_database: str, uniprot_accs: List[str]) -> Dict:
    """
    Perform a mapping of Uniprot accessions to another database.
    
    Args:
        ctx: The run context
        target_database: The target database (e.g KEGG, PDB)
        uniprot_accs: The Uniprot accessions
        
    Returns:
        Dict: Mapping results
    """
    print(f"UNIPROT MAPPING: {target_database} - {uniprot_accs}")
    try:
        uniprot_service = ctx.deps.get_uniprot_service()
        normalized_accs = [normalize_uniprot_id(x) for x in uniprot_accs]
        result = uniprot_service.mapping("UniProtKB_AC-ID", target_database, ",".join(normalized_accs))
        
        if not result or len(result) == 0:
            raise ModelRetry(f"No mappings found for {uniprot_accs} to {target_database}. Try a different database or accessions.")
            
        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error mapping {uniprot_accs} to {target_database}: {str(e)}")
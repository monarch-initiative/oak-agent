"""
DEPRECATED: This module has been refactored into the amigo/ subdirectory.

This file remains for backward compatibility, but you should use:
- aurelian.agents.amigo.amigo_agent
- aurelian.agents.amigo.amigo_config
- aurelian.agents.amigo.amigo_tools
- aurelian.agents.amigo.amigo_gradio
"""

# Re-export from new location
from aurelian.agents.amigo.amigo_agent import amigo_agent
from aurelian.agents.amigo.amigo_config import AmiGODependencies, normalize_pmid
from aurelian.agents.amigo.amigo_tools import (
    find_gene_associations,
    find_gene_associations_for_pmid,
    lookup_uniprot_entry,
    uniprot_mapping
)
from aurelian.agents.amigo.amigo_gradio import chat

# For backward compatibility with tests
from oaklib.implementations import AmiGOImplementation
from oaklib.datamodels.association import Association, NegatedAssociation
from oaklib.implementations.amigo.amigo_implementation import (
    DEFAULT_SELECT_FIELDS, QUALIFIER, BIOENTITY,
    BIOENTITY_LABEL, map_predicate, ANNOTATION_CLASS, ANNOTATION_CLASS_LABEL, 
    REFERENCE, EVIDENCE_TYPE, ASSIGNED_BY,
    _query as amigo_query,
    _normalize
)
from aurelian.utils.data_utils import obj_to_dict

def get_amigo_adapter(ctx):
    return ctx.deps.get_amigo_adapter()

def get_gene_id(ctx, gene_term):
    return ctx.deps.get_gene_id(gene_term)

def gene_associations(ctx, gene_id):
    """Kept for backward compatibility, use find_gene_associations instead."""
    from aurelian.utils.async_utils import run_sync
    return run_sync(lambda: find_gene_associations(ctx, gene_id))

def gene_associations_for_pmid(amigo, pmid):
    """
    Find gene associations for a given PMID - kept for backward compatibility.
    
    Args:
        amigo: OAK AmiGO endpoint
        pmid: The PMID
        
    Returns:
        List of gene associations
    """
    print(f"Lookup amigo annotations to PMID: {pmid}")
    solr = amigo._solr
    select_fields = DEFAULT_SELECT_FIELDS
    results = amigo_query(solr, {"reference": pmid}, select_fields)
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
    return assocs

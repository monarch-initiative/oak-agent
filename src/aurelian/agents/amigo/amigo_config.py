"""
Configuration classes for the AmiGO agent.
"""
from dataclasses import dataclass, field

from bioservices import UniProt
from oaklib import get_adapter
from oaklib.implementations import AmiGOImplementation

from aurelian.dependencies.workdir import HasWorkdir
from aurelian.agents.uniprot.uniprot_tools import normalize_uniprot_id

# Initialize UniProt service
uniprot_service = UniProt(verbose=False)


@dataclass
class AmiGODependencies(HasWorkdir):
    """
    Configuration for the AmiGO agent.
    
    Args:
        taxon: NCBI Taxonomy ID, defaults to human (9606)
    """
    taxon: str = field(default="9606")
    
    def get_uniprot_service(self) -> UniProt:
        """
        Get the UniProt service for protein lookups.
        
        Returns:
            UniProt: The UniProt service
        """
        return uniprot_service
    
    def get_amigo_adapter(self) -> AmiGOImplementation:
        """
        Get the AmiGO adapter for the specified taxon.
        
        Returns:
            AmiGOImplementation: The OAK AmiGO adapter
        """
        return get_adapter(f"amigo:NCBITaxon:{self.taxon}")
        
    def get_gene_id(self, gene_term: str) -> str:
        """
        Normalize a gene identifier.
        
        Args:
            gene_term: The gene identifier
            
        Returns:
            str: The normalized gene identifier
        """
        return gene_term


def normalize_pmid(pmid: str) -> str:
    """
    Normalize a PubMed ID to the format PMID:nnnnnnn.
    
    Args:
        pmid: The PubMed ID
        
    Returns:
        str: The normalized PubMed ID
    """
    if ":" in pmid:
        pmid = pmid.split(":", 1)[1]
    if not pmid.startswith("PMID:"):
        pmid = f"PMID:{pmid}"
    return pmid


def get_config(taxon: str = "9606") -> AmiGODependencies:
    """
    Get the AmiGO configuration.
    
    Args:
        taxon: NCBI Taxonomy ID, defaults to human (9606)
        
    Returns:
        AmiGODependencies: The AmiGO dependencies
    """
    return AmiGODependencies(taxon=taxon)
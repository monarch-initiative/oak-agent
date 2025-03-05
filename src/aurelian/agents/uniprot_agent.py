"""
Agent for working with uniprot API endpoint
"""
from dataclasses import dataclass
from typing import Dict, List

from bioservices import UniProt
from pydantic_ai import Agent, RunContext


@dataclass
class Dependencies:
    pass


u = UniProt(verbose=False)

uniprot_agent = Agent(
    model="openai:gpt-4o",
)


def normalize_uniprot_id(uniprot_id: str) -> str:
    """Normalize a Uniprot ID by removing any version number

    Args:
        uniprot_id: The Uniprot ID

    """
    if ":" in uniprot_id:
        return uniprot_id.split(":")[-1]
    return uniprot_id


@uniprot_agent.tool
def search(ctx: RunContext[Dependencies], query: str) -> str:
    return u.search(query, frmt="tsv", columns="accession,id,gene_names")


@uniprot_agent.tool
def lookup_uniprot_entry(ctx: RunContext[Dependencies], uniprot_acc: str) -> str:
    """Lookup the Uniprot entry for a given Uniprot accession number

    Args:
        uniprot_acc: The Uniprot accession

    """
    uniprot_acc = normalize_uniprot_id(uniprot_acc)
    return u.retrieve(uniprot_acc, frmt="txt")


@uniprot_agent.tool
def uniprot_mapping(ctx: RunContext[Dependencies], target_database: str, uniprot_accs: List[str]) -> Dict:
    """Perform a mapping of Uniprot accessions to another database

    Args:
        target_database: The target database (e.g KEGG, PDB)
        uniprot_accs: The Uniprot accessions

    """
    uniprot_accs = [normalize_uniprot_id(x) for x in uniprot_accs]
    return u.mapping("UniProtKB_AC-ID", target_database, ",".join(uniprot_accs))

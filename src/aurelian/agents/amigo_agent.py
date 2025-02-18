from dataclasses import dataclass
from typing import List, Dict, Union

from dataclasses import dataclass
from bioservices import UniProt
from linkml_runtime.dumpers import json_dumper
from linkml_runtime.utils.yamlutils import YAMLRoot
from oaklib import get_adapter
from oaklib.implementations import AmiGOImplementation
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from aurelian.agents.uniprot_agent import normalize_uniprot_id

u = UniProt()

@dataclass
class AmiGODependencies:
    taxon: str = "9606"

amigo_agent = Agent(
    model="openai:gpt-4o",
)

def obj_to_dict(obj: Union[object, YAMLRoot, BaseModel, Dict]) -> Dict:
    if isinstance(obj, YAMLRoot):
        return json_dumper.to_dict(obj)
    elif isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return obj
    else:
        raise ValueError(f"Cannot convert object of type {type(obj)} to dict")


def get_amigo_adapter(ctx: RunContext[AmiGODependencies]) -> AmiGOImplementation:
    taxon = ctx.deps.taxon
    return get_adapter(f"amigo:NCBITaxon:{taxon}")


def get_gene_id(ctx: RunContext[AmiGODependencies], gene_term: str) -> str:
    return gene_term


def gene_associations(ctx: RunContext[AmiGODependencies], gene_id: str) -> List[Dict]:
    """
    Retrieve gene associations for a given gene

    Args:
        ctx: The run context
        gene_id: The gene ID
    """
    adapter = get_amigo_adapter(ctx)
    normalized_gene_id = get_gene_id(ctx, gene_id)
    assocs = [obj_to_dict(a) for a in adapter.associations([normalized_gene_id])]
    return assocs

@amigo_agent.tool
def find_gene_associations(ctx: RunContext[AmiGODependencies], gene_id: str) -> List[Dict]:
    return gene_associations(ctx, gene_id)


@amigo_agent.tool
def lookup_uniprot_entry(ctx: RunContext[AmiGODependencies], uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number

    Args:
        uniprot_acc: The Uniprot accession
    """
    uniprot_acc = normalize_uniprot_id(uniprot_acc)
    return u.retrieve(uniprot_acc, frmt="txt")


@amigo_agent.tool
def uniprot_mapping(ctx: RunContext[AmiGODependencies], target_database: str, uniprot_accs: List[str]) -> Dict:
    """
    Perform a mapping of Uniprot accessions to another database

    Args:
        target_database: The target database (e.g KEGG, PDB)
        uniprot_accs: The Uniprot accessions
    """
    uniprot_accs = [normalize_uniprot_id(x) for x in uniprot_accs]
    return u.mapping("UniProtKB_AC-ID", target_database, ",".join(uniprot_accs))
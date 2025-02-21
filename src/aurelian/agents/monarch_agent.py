from dataclasses import dataclass
from typing import List, Dict, Union

from dataclasses import dataclass
from oaklib import get_adapter
from oaklib.interfaces import OboGraphInterface
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext



@dataclass
class MonarchDependencies:
    taxon: str = "9606"

monarch_agent = Agent(
    model="openai:gpt-4o",
)



def get_monarch_adapter(ctx: RunContext[MonarchDependencies]) -> OboGraphInterface:
    return get_adapter(f"monarch:")

def get_mondo_adapter(ctx: RunContext[MonarchDependencies]) -> OboGraphInterface:
    return get_adapter(f"sqlite:obo:mondo")

def get_gene_id(ctx: RunContext[MonarchDependencies], gene_term: str) -> str:
    return gene_term



@monarch_agent.tool
def find_gene_associations(ctx: RunContext[MonarchDependencies], gene_id: str) -> List[Dict]:
    adapter = get_monarch_adapter(ctx)
    normalized_gene_id = get_gene_id(ctx, gene_id)
    assocs = [obj_to_dict(a) for a in adapter.associations([normalized_gene_id])]
    return assocs

def get_disease_id(ctx: RunContext[MonarchDependencies], term: str) -> str:
    return term

@monarch_agent.tool
def find_disease_associations(ctx: RunContext[MonarchDependencies], disease_id: str) -> List[Dict]:
    adapter = get_monarch_adapter(ctx)
    normalized_disease_id = get_disease_id(ctx, disease_id)
    assocs = [obj_to_dict(a) for a in adapter.associations([normalized_disease_id])]
    return assocs

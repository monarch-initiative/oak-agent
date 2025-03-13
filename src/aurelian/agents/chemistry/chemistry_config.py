"""
Configuration classes for the chemistry agent.
"""
from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel
from aurelian.dependencies.workdir import HasWorkdir


class ChemicalStructure(BaseModel):
    """
    Model for representing chemical structures.
    """
    chebi_id: Optional[str] = None
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    name: Optional[str] = None

    @property
    def chebi_local_id(self) -> Optional[str]:
        if self.chebi_id:
            return self.chebi_id.split(":")[1]
        return None

    @property
    def chebi_image_url(self) -> str:
        local_id = self.chebi_local_id
        if local_id:
            return f"https://www.ebi.ac.uk/chebi/displayImage.do?defaultImage=true&imageIndex=0&chebiId={local_id}"
        return ""

    @classmethod
    def from_id(cls, id: str) -> 'ChemicalStructure':
        if ":" in id:
            prefix, local_id = id.split(":")
            if prefix.lower() != "chebi":
                raise ValueError(f"Invalid prefix: {prefix}")
            id = "CHEBI:" + local_id
        else:
            id = "CHEBI:" + id
        return cls(chebi_id=id)

    @classmethod
    def from_anything(cls, id: str) -> 'ChemicalStructure':
        if ":" in id:
            return cls.from_id(id)
        # check if valid smiles
        from rdkit import Chem
        mol = Chem.MolFromSmiles(id)
        if mol:
            return cls(smiles=id)
        raise ValueError(f"Invalid identifier: {id}")


@dataclass
class ChemistryDependencies(HasWorkdir):
    """
    Configuration for the chemistry agent.
    """
    max_search_results: int = 30


def get_config() -> ChemistryDependencies:
    """
    Get the Chemistry agent configuration.
    
    Returns:
        ChemistryDependencies: The chemistry dependencies
    """
    return ChemistryDependencies()
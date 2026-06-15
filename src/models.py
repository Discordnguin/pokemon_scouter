from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Pokemon:
    species: str
    types: List[str] = field(default_factory=list)
    is_mega: bool = False
    
    @property
    def export_name(self) -> str:
        # Formats the name for the importable output
        if self.is_mega and not self.species.endswith("-Mega"):
            return f"{self.species}-Mega"
        return self.species

    def has_type(self, type_name: str) -> bool:
        return type_name in self.types

@dataclass
class Team:
    player: str
    roster: List[Pokemon]
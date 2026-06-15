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
        if self.is_mega:
            # If the species string already indicates the Mega variant (e.g. "Charizard-Mega-X"),
            # return it verbatim. Otherwise append the generic "-Mega" suffix.
            if "Mega" in self.species:
                return self.species
            return f"{self.species}-Mega"
        return self.species

    def has_type(self, type_name: str) -> bool:
        return type_name in self.types

@dataclass
class Team:
    player: str
    roster: List[Pokemon]

@dataclass
class MatchScout:
    player: str
    opponent: str
    tour: str
    result: str
    z_move_user: str
    team: Team
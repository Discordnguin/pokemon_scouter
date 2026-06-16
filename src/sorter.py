from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from src.models import Pokemon, Team

SlotCondition = Callable[[Pokemon], bool]

# --- Constants & Type Effectiveness Dictionaries ---

GROUND_EFFECTIVENESS = {
    'Normal': 1, 'Fire': 2, 'Water': 1, 'Electric': 0, 'Grass': 0.5,
    'Ice': 1, 'Fighting': 1, 'Poison': 1, 'Ground': 1, 'Flying': 0,
    'Psychic': 1, 'Bug': 0.5, 'Rock': 2, 'Ghost': 1, 'Dragon': 1,
    'Dark': 1, 'Steel': 2, 'Fairy': 1,
}

GROUND_OFFENSE_VS_GROUND = {
    'Normal': 1, 'Fire': 1, 'Water': 2, 'Electric': 0, 'Grass': 2,
    'Ice': 2, 'Fighting': 1, 'Poison': 0.5, 'Ground': 1, 'Flying': 1,
    'Psychic': 1, 'Bug': 0.5, 'Rock': 1, 'Ghost': 1, 'Dragon': 1,
    'Dark': 1, 'Steel': 1, 'Fairy': 1,
}

WATER_EFFECTIVENESS = {
    'Normal': 1, 'Fire': 2, 'Water': 0.5, 'Electric': 1, 'Grass': 0.5,
    'Ice': 1, 'Fighting': 1, 'Poison': 1, 'Ground': 2, 'Flying': 1,
    'Psychic': 1, 'Bug': 1, 'Rock': 2, 'Ghost': 1, 'Dragon': 0.5,
    'Dark': 1, 'Steel': 0.5, 'Fairy': 1,
}

STEEL_PRIORITY = [
    'Magearna', 'Jirachi', 'Heatran', 'Ferrothorn', 'Celesteela', 'Magnezone',
]


# --- Shared Helper Functions ---

def get_type_effectiveness(mon: Pokemon, effectiveness: dict[str, float]) -> float:
    score = 1.0
    for typ in mon.types:
        score *= effectiveness.get(typ, 1)
    return score

def is_water_resist(mon: Pokemon) -> bool:
    return get_type_effectiveness(mon, WATER_EFFECTIVENESS) < 1

def is_ground_resist(mon: Pokemon) -> bool:
    return get_type_effectiveness(mon, GROUND_EFFECTIVENESS) < 1

def best_ground_resist_candidate(unassigned: List[Pokemon]) -> Optional[Pokemon]:
    if not unassigned:
        return None

    def rank(mon: Pokemon) -> tuple[int, float, float]:
        defense = get_type_effectiveness(mon, GROUND_EFFECTIVENESS)
        # Offense vs Ground
        offense = 1.0
        for typ in mon.types:
            offense *= GROUND_OFFENSE_VS_GROUND.get(typ, 1)
            
        if defense < 1:
            category = 0
        elif defense == 1:
            category = 1
        else:
            category = 2
        return (category, -offense, defense)

    return min(unassigned, key=rank)


# --- Strategy Interface ---

class SortingStrategy(ABC):
    @property
    def allows_megas(self) -> bool:
        """Determines if the tier supports Mega Evolution."""
        return False

    @abstractmethod
    def apply_custom_overrides(self, sorter: "TeamSorter") -> None:
        """Apply any hardcoded pairings/overrides before standard slotting."""
        pass

    @abstractmethod
    def get_slot_conditions(self, sorter: "TeamSorter") -> List[SlotCondition]:
        """Return the ordered list of conditions to evaluate."""
        pass


# --- Gen 6 OU Strategy ---

class Gen6Strategy(SortingStrategy):
    @property
    def allows_megas(self) -> bool:
        return True

    def apply_custom_overrides(self, sorter: "TeamSorter") -> None:
        species_list = [m.species for m in sorter.unassigned]
        if 'Swampert' in species_list and 'Pelipper' in species_list:
            pelipper = sorter._extract_by_condition(lambda mon: mon.species == 'Pelipper')
            swampert = sorter._extract_by_condition(lambda mon: mon.species == 'Swampert')
            if pelipper: sorter.ordered_roster.append(pelipper)
            if swampert: sorter.ordered_roster.append(swampert)

    def get_slot_conditions(self, sorter: "TeamSorter") -> List[SlotCondition]:
        return [
            lambda m: m.is_mega,
            lambda m: self._pick_primary_ground(sorter.unassigned, m),
            lambda m: self._pick_steel_slot(sorter.unassigned, m),
            lambda m: self._pick_water_resist(sorter.unassigned, m),
            lambda m: self._pick_water_fallback(sorter.unassigned, m),
            lambda m: self._pick_ground_resist_slot(sorter.unassigned, m),
            lambda m: self._pick_other_steel(sorter.unassigned, m),
            lambda m: m.has_type('Flying') or m.has_type('Bug') or m.has_type('Grass'),
        ]

    def _pick_primary_ground(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        grounds = [m for m in unassigned if m.has_type('Ground')]
        best = None
        if grounds:
            best = next((m for m in grounds if m.species == 'Landorus-Therian'), grounds[0])
        elif any(m.species == 'Thundurus-Therian' for m in unassigned):
            best = next(m for m in unassigned if m.species == 'Thundurus-Therian')
        else:
            grasses = [m for m in unassigned if m.has_type('Grass')]
            best = grasses[0] if grasses else None
            
        return best is not None and mon is best

    def _pick_steel_slot(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        if not mon.has_type('Steel'):
            return False
        if mon.species in STEEL_PRIORITY:
            return True
        if mon.species == 'Kartana':
            remaining_steel = [m for m in unassigned if m.has_type('Steel') and m.species != 'Kartana']
            return not any(remaining_steel)
        return True

    def _pick_water_resist(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        water_types = [m for m in unassigned if m.has_type('Water')]
        if water_types:
            best = water_types[0]
        else:
            water_resists = [m for m in unassigned if is_water_resist(m)]
            if water_resists:
                best = min(water_resists, key=lambda m: get_type_effectiveness(m, WATER_EFFECTIVENESS))
            else:
                best = next((m for m in unassigned if m.species == 'Chansey'), None)
        return best is not None and mon is best

    def _pick_ground_resist_slot(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        best = best_ground_resist_candidate(unassigned)
        return best is not None and mon is best

    def _pick_water_fallback(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        if any(m.has_type('Water') or is_water_resist(m) for m in unassigned):
            return False
        return mon.species == 'Chansey'

    def _pick_other_steel(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        if not mon.has_type('Steel') or mon.species == 'Kartana':
            return False
        return True


# --- Gen 7 OU Strategy ---

class Gen7Strategy(SortingStrategy):
    @property
    def allows_megas(self) -> bool:
        return True

    def apply_custom_overrides(self, sorter: "TeamSorter") -> None:
        species_list = [m.species for m in sorter.unassigned]
        if 'Swampert' in species_list and 'Pelipper' in species_list:
            pelipper = sorter._extract_by_condition(lambda mon: mon.species == 'Pelipper')
            swampert = sorter._extract_by_condition(lambda mon: mon.species == 'Swampert')
            if pelipper: sorter.ordered_roster.append(pelipper)
            if swampert: sorter.ordered_roster.append(swampert)

    def get_slot_conditions(self, sorter: "TeamSorter") -> List[SlotCondition]:
        return [
            lambda m: m.is_mega,
            lambda m: self._pick_primary_ground(sorter.unassigned, m),
            lambda m: self._pick_steel_slot(sorter.unassigned, m),
            lambda m: self._pick_water_resist(sorter.unassigned, m),
            lambda m: self._pick_water_fallback(sorter.unassigned, m),
            lambda m: self._pick_ground_resist_slot(sorter.unassigned, m),
            lambda m: self._pick_other_steel(sorter.unassigned, m),
            lambda m: m.has_type('Flying') or m.has_type('Bug') or m.has_type('Grass'),
        ]

    def _pick_primary_ground(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        grounds = [m for m in unassigned if m.has_type('Ground')]
        best = None
        if grounds:
            best = next((m for m in grounds if m.species == 'Landorus-Therian'), grounds[0])
        elif any(m.species == 'Thundurus-Therian' for m in unassigned):
            best = next(m for m in unassigned if m.species == 'Thundurus-Therian')
        else:
            grasses = [m for m in unassigned if m.has_type('Grass')]
            best = grasses[0] if grasses else None
            
        return best is not None and mon is best

    def _pick_steel_slot(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        if not mon.has_type('Steel'):
            return False
        if mon.species in STEEL_PRIORITY:
            return True
        if mon.species == 'Kartana':
            remaining_steel = [m for m in unassigned if m.has_type('Steel') and m.species != 'Kartana']
            return not any(remaining_steel)
        return True

    def _pick_water_resist(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        water_types = [m for m in unassigned if m.has_type('Water')]
        if water_types:
            best = water_types[0]
        else:
            water_resists = [m for m in unassigned if is_water_resist(m)]
            if water_resists:
                best = min(water_resists, key=lambda m: get_type_effectiveness(m, WATER_EFFECTIVENESS))
            else:
                best = next((m for m in unassigned if m.species == 'Chansey'), None)
        return best is not None and mon is best

    def _pick_ground_resist_slot(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        best = best_ground_resist_candidate(unassigned)
        return best is not None and mon is best

    def _pick_water_fallback(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        if any(m.has_type('Water') or is_water_resist(m) for m in unassigned):
            return False
        return mon.species == 'Chansey'

    def _pick_other_steel(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        if not mon.has_type('Steel') or mon.species == 'Kartana':
            return False
        return True


# --- Gen 8 OU Strategy ---

class Gen8Strategy(SortingStrategy):
    def apply_custom_overrides(self, sorter: "TeamSorter") -> None:
        # Define any Gen 8 specific pair overrides here in the future
        pass

    def get_slot_conditions(self, sorter: "TeamSorter") -> List[SlotCondition]:
        return [
            lambda m: self._pick_ground_type(sorter.unassigned, m),
            lambda m: self._pick_steel_type(sorter.unassigned, m),
            lambda m: self._pick_water_resist(sorter.unassigned, m),
            lambda m: self._pick_ghost_resist(sorter.unassigned, m),
            lambda m: self._pick_ground_resist(sorter.unassigned, m)
        ]

    def _pick_ground_type(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        grounds = [m for m in unassigned if m.has_type('Ground')]
        return grounds and mon is grounds[0]

    def _pick_steel_type(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        steels = [m for m in unassigned if m.has_type('Steel')]
        if not steels:
            return False

        best = next((m for m in steels if m.species != 'Kartana'), steels[0])
        return mon is best

    def _pick_water_resist(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        water_resists = [m for m in unassigned if m.has_type('Water') or is_water_resist(m)]
        if not water_resists:
            return False

        # Prioritize true water types first, then Dragapult, then best water resist.
        true_waters = [m for m in water_resists if m.has_type('Water')]
        if true_waters:
            best = true_waters[0]
        else:
            dragapult = next((m for m in water_resists if m.species == 'Dragapult'), None)
            if dragapult:
                best = dragapult
            else:
                best = min(water_resists, key=lambda m: get_type_effectiveness(m, WATER_EFFECTIVENESS))
        return mon is best

    def _pick_ghost_resist(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        # 1. Look for Normal or Dark, excluding Ditto. Include Kommo-o (Bulletproof).
        primary_resists = [
            m for m in unassigned 
            if (m.has_type('Dark') or m.has_type('Normal') or m.species == 'Kommo-o') and m.species != 'Ditto'
        ]
        
        if primary_resists:
            return mon is primary_resists[0]
            
        # 2. Fallback to Fairy type
        fairies = [m for m in unassigned if m.has_type('Fairy')]
        if not fairies:
            return False
            
        # Prioritize Clefable
        clefable = next((m for m in fairies if m.species == 'Clefable'), None)
        if clefable:
            return mon is clefable
            
        # Deprioritize Tapu Lele and Tapu Bulu
        standard_fairies = [m for m in fairies if m.species not in ['Tapu Lele', 'Tapu Bulu']]
        best = standard_fairies[0] if standard_fairies else fairies[0]
        return mon is best

    def _pick_ground_resist(self, unassigned: List[Pokemon], mon: Pokemon) -> bool:
        best = best_ground_resist_candidate(unassigned)
        return best is not None and mon is best


# --- Main Context Sorter ---

class TeamSorter:
    def __init__(self, team: Team, strategy: SortingStrategy):
        self.team = team
        self.strategy = strategy
        self.unassigned: List[Pokemon] = []
        self.ordered_roster: List[Pokemon] = []

    def _reset(self) -> None:
        self.unassigned = self.team.roster.copy()
        self.ordered_roster = []
        if not self.strategy.allows_megas:
            for mon in self.unassigned:
                mon.is_mega = False

    def _extract_by_condition(self, condition: SlotCondition) -> Optional[Pokemon]:
        for mon in self.unassigned:
            if condition(mon):
                self.unassigned.remove(mon)
                return mon
        return None

    def sort_scout(self) -> List[str]:
        self._reset()
        
        # 1. Process custom overrides dictated by the current tier strategy
        self.strategy.apply_custom_overrides(self)

        # 2. Iterate dynamically over the tier strategy's target slots
        conditions = self.strategy.get_slot_conditions(self)
        for condition in conditions:
            mon = self._extract_by_condition(condition)
            if mon:
                self.ordered_roster.append(mon)

        # 3. Filler slots
        self.ordered_roster.extend(self.unassigned)
        
        return [mon.export_name for mon in self.ordered_roster]
from typing import Callable, List, Optional

from src.models import Pokemon, Team

SlotCondition = Callable[[Pokemon], bool]

# Attacking type effectiveness against a defending mon.
GROUND_EFFECTIVENESS = {
    'Normal': 1,
    'Fire': 2,
    'Water': 1,
    'Electric': 0,
    'Grass': 0.5,
    'Ice': 1,
    'Fighting': 1,
    'Poison': 1,
    'Ground': 1,
    'Flying': 0,
    'Psychic': 1,
    'Bug': 0.5,
    'Rock': 2,
    'Ghost': 1,
    'Dragon': 1,
    'Dark': 1,
    'Steel': 2,
    'Fairy': 1,
}

# type effectiveness attacking against a ground type
GROUND_OFFENSE_VS_GROUND = {
    'Normal': 1,
    'Fire': 1,
    'Water': 2,
    'Electric': 0,
    'Grass': 2,
    'Ice': 2,
    'Fighting': 1,
    'Poison': 0.5,
    'Ground': 1,
    'Flying': 1,
    'Psychic': 1,
    'Bug': 0.5,
    'Rock': 1,
    'Ghost': 1,
    'Dragon': 1,
    'Dark': 1,
    'Steel': 1,
    'Fairy': 1,
}

WATER_EFFECTIVENESS = {
    'Normal': 1,
    'Fire': 2,
    'Water': 0.5,
    'Electric': 1,
    'Grass': 0.5,
    'Ice': 1,
    'Fighting': 1,
    'Poison': 1,
    'Ground': 2,
    'Flying': 1,
    'Psychic': 1,
    'Bug': 1,
    'Rock': 2,
    'Ghost': 1,
    'Dragon': 0.5,
    'Dark': 1,
    'Steel': 0.5,
    'Fairy': 1,
}

STEEL_PRIORITY = [
    'Magearna',
    'Jirachi',
    'Heatran',
    'Ferrothorn',
    'Celesteela',
]

class TeamSorter:
    def __init__(self, team: Team, slot_conditions: Optional[List[SlotCondition]] = None):
        self.team = team
        self.slot_conditions = slot_conditions or self.default_slot_conditions()
        self.unassigned: List[Pokemon] = []
        self.ordered_roster: List[Pokemon] = []

    def _reset(self) -> None:
        self.unassigned = self.team.roster.copy()
        self.ordered_roster = []

    def _extract_by_condition(self, condition: SlotCondition) -> Optional[Pokemon]:
        for mon in self.unassigned:
            if condition(mon):
                self.unassigned.remove(mon)
                return mon
        return None

    def default_slot_conditions(self) -> List[SlotCondition]:
        return [
            self._pick_mega,
            self._pick_primary_ground,
            self._pick_steel_slot,
            self._pick_water_resist,
            self._pick_ground_resist_slot,
            self._pick_other_steel,
            self._pick_flying_or_bug,
        ]

    def _pick_mega(self, mon: Pokemon) -> bool:
        return mon.is_mega

    def _pick_primary_ground(self, mon: Pokemon) -> bool:
        # Prefer Landorus-Therian first, then Thundurus-Therian, then any Grass type.
        if mon.species.lower() == 'landorus-therian':
            return True
        if any(m.species.lower() == 'landorus-therian' for m in self.unassigned):
            return False
        if mon.species.lower() == 'thundurus-therian':
            return True
        if any(m.species.lower() == 'thundurus-therian' for m in self.unassigned):
            return False
        return mon.has_type('Grass')

    def _pick_steel_slot(self, mon: Pokemon) -> bool:
        # Steel slot should prefer Magearna/Jirachi/Heatran/Ferrothorn/Celesteela first,
        # otherwise choose Kartana only if no other steel remains.
        if not mon.has_type('Steel'):
            return False
        if mon.species in STEEL_PRIORITY:
            return True
        if mon.species == 'Kartana':
            remaining_steel = [m for m in self.unassigned if m.has_type('Steel') and m.species != 'Kartana']
            return not any(remaining_steel)
        return True

    def _pick_water_resist(self, mon: Pokemon) -> bool:
        # Prefer actual Water types first; otherwise choose the best water resist.
        best = self._best_water_resist_candidate()
        return best is not None and mon is best

    def _pick_ground_resist_slot(self, mon: Pokemon) -> bool:
        best = self._best_ground_resist_candidate()
        return best is not None and mon is best

    def _pick_other_steel(self, mon: Pokemon) -> bool:
        # Place remaining non-Kartana steel types after the water slot.
        if not mon.has_type('Steel'):
            return False
        if mon.species == 'Kartana':
            return False
        return True

    def _best_water_resist_candidate(self) -> Optional[Pokemon]:
        water_types = [m for m in self.unassigned if m.has_type('Water')]
        if water_types:
            return water_types[0]
        water_resists = [m for m in self.unassigned if self._is_water_resist(m)]
        if not water_resists:
            return None
        return min(water_resists, key=lambda m: self._type_effectiveness(m, WATER_EFFECTIVENESS))

    def _offense_vs_ground(self, mon: Pokemon) -> float:
        score = 1.0
        for typ in mon.types:
            score *= GROUND_OFFENSE_VS_GROUND.get(typ, 1)
        return score

    def _best_ground_resist_candidate(self) -> Optional[Pokemon]:
        if not self.unassigned:
            return None

        def rank(mon: Pokemon) -> tuple[int, float, float]:
            defense = self._type_effectiveness(mon, GROUND_EFFECTIVENESS)
            offense = self._offense_vs_ground(mon)
            if defense < 1:
                category = 0
            elif defense == 1:
                category = 1
            else:
                category = 2
            return (category, -offense, defense)

        return min(self.unassigned, key=rank)

    def _pick_flying_or_bug(self, mon: Pokemon) -> bool:
        return mon.has_type('Flying') or mon.has_type('Bug') or mon.has_type('Grass')

    def _type_effectiveness(self, mon: Pokemon, effectiveness: dict[str, float]) -> float:
        score = 1.0
        for typ in mon.types:
            score *= effectiveness.get(typ, 1)
        return score

    def _is_water_resist(self, mon: Pokemon) -> bool:
        return self._type_effectiveness(mon, WATER_EFFECTIVENESS) < 1

    def _is_ground_resist(self, mon: Pokemon) -> bool:
        return self._type_effectiveness(mon, GROUND_EFFECTIVENESS) < 1

    def _is_ground_weak(self, mon: Pokemon) -> bool:
        return self._type_effectiveness(mon, GROUND_EFFECTIVENESS) > 1

    def _best_ground_choice(self) -> Optional[Pokemon]:
        resistors = [m for m in self.unassigned if not self._is_ground_weak(m)]
        if resistors:
            return min(resistors, key=lambda m: (self._type_effectiveness(m, GROUND_EFFECTIVENESS), 'Ice' not in m.types))
        return min(self.unassigned, key=lambda m: ('Ice' not in m.types, self._type_effectiveness(m, GROUND_EFFECTIVENESS)))

    def _apply_custom_overrides(self) -> None:
        if any(mon.species == 'Swampert' for mon in self.unassigned) and any(mon.species == 'Pelipper' for mon in self.unassigned):
            pelipper = self._extract_by_condition(lambda mon: mon.species == 'Pelipper')
            swampert = self._extract_by_condition(lambda mon: mon.species == 'Swampert')
            if pelipper:
                self.ordered_roster.append(pelipper)
            if swampert:
                self.ordered_roster.append(swampert)

    def sort_scout(self, slot_conditions: Optional[List[SlotCondition]] = None) -> List[str]:
        self._reset()
        conditions = slot_conditions or self.slot_conditions

        self._apply_custom_overrides()

        for condition in conditions:
            mon = self._extract_by_condition(condition)
            if mon:
                self.ordered_roster.append(mon)

        self.ordered_roster.extend(self.unassigned)
        return [mon.export_name for mon in self.ordered_roster]

from typing import Callable, List, Optional

from src.models import Pokemon, Team

SlotCondition = Callable[[Pokemon], bool]

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
            lambda mon: mon.is_mega,
            lambda mon: mon.has_type('Ground'),
            lambda mon: mon.has_type('Steel'),
            lambda mon: mon.has_type('Water') or mon.has_type('Grass') or mon.has_type('Dragon'),
            lambda mon: mon.has_type('Flying') or mon.has_type('Bug') or mon.has_type('Grass'),
        ]

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

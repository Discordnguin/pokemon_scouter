import requests
from typing import Dict, List, Optional

from src.models import Pokemon, Team, MatchScout

class ShowdownParser:
    def __init__(self, target_usernames: List[str], dex_config: Dict[str, Dict[str, List[str]]]):
        self.targets = [username.lower() for username in target_usernames]
        self.dex_config = dex_config

    def parse_replay(self, replay_url: str, tour_name: str) -> List[MatchScout]:
        log_url = replay_url if replay_url.endswith('.log') else f"{replay_url}.log"
        response = requests.get(log_url)
        response.raise_for_status()
        log_lines = response.text.splitlines()

        players: Dict[str, str] = {}
        teams_raw: Dict[str, List[str]] = {'p1': [], 'p2': []}
        megas: Dict[str, set] = {'p1': set(), 'p2': set()}
        # Map p1/p2 -> base species -> variant name (e.g. Charizard -> Charizard-Mega-Y)
        megas_variant_map: Dict[str, Dict[str, str]] = {'p1': {}, 'p2': {}}
        z_move_users: Dict[str, List[str]] = {'p1': [], 'p2': []}
        win_player: Optional[str] = None
        
        # Track Greninja behavior: {p_id: {'used_move': bool, 'showed_protean': bool}}
        greninja_behavior: Dict[str, Dict[str, bool]] = {'p1': {'used_move': False, 'showed_protean': False}, 'p2': {'used_move': False, 'showed_protean': False}}

        for i, line in enumerate(log_lines):
            parts = line.split('|')
            if len(parts) < 2:
                continue

            # Example: "|player|p1|Yelodash|..." -> capture mapping p1 -> 'yelodash'
            if parts[1] == 'player' and len(parts) > 3:
                p_id, p_name = parts[2], parts[3].lower()
                # Avoid overwriting a previously parsed non-empty username with
                # later blank |player|...| lines that appear in some logs.
                if p_name.strip():
                    players[p_id] = p_name

            # Example: "|poke|p1|Aerodactyl, M|item" -> capture species listed in preview
            elif parts[1] == 'poke' and len(parts) > 3:
                p_id = parts[2]
                # parts[3] can include extra CSV info; species is the first token
                species = parts[3].split(',')[0].strip()
                if p_id in teams_raw:
                    teams_raw[p_id].append(species)

            # Example: "|-mega|p1a: Aerodactyl|Aerodactyl|Aerodactylite"
            # We normalize p1a/p1b/etc. back to p1/p2 so we can mark the species
            elif parts[1] == '-mega' and len(parts) > 3:
                p_id = parts[2].split(':')[0]
                if p_id.startswith('p1'):
                    p_id = 'p1'
                elif p_id.startswith('p2'):
                    p_id = 'p2'
                species_who_megaed = parts[3].strip()
                # parts[3] is usually the base species; record it so we know which
                # preview entry mega-evolved.
                if p_id in megas:
                    megas[p_id].add(species_who_megaed)

            elif parts[1] == 'detailschange' and len(parts) > 3:
                # detailschange lines often contain the Mega form name, e.g.
                # |detailschange|p2a: Charizard|Charizard-Mega-Y, M
                slot = parts[2].split(':', 1)[0]
                slot_player = 'p1' if slot.startswith('p1') else 'p2'
                base_species = parts[2].split(':', 1)[1].strip() if ':' in parts[2] else ''
                variant = parts[3].split(',')[0].strip()
                
                # Track if Greninja showed a type change (Protean activation)
                if base_species and base_species.startswith('Greninja'):
                    if greninja_behavior[slot_player]['used_move']:
                        greninja_behavior[slot_player]['showed_protean'] = True
                
                if base_species and variant and variant != base_species:
                    existing_variant = megas_variant_map.setdefault(slot_player, {}).get(base_species)
                    if not existing_variant or existing_variant == base_species:
                        megas_variant_map[slot_player][base_species] = variant

            elif parts[1] == 'move' and len(parts) > 3:
                # |move|p1a: Greninja|Water Shuriken|...
                # Track if Greninja used a move
                slot = parts[2].split(':', 1)[0]
                slot_player = 'p1' if slot.startswith('p1') else 'p2'
                mon_species = parts[2].split(':', 1)[1].strip() if ':' in parts[2] else ''
                
                if mon_species.startswith('Greninja'):
                    greninja_behavior[slot_player]['used_move'] = True

            elif parts[1] == '-zpower' and len(parts) > 2:
                p_id = parts[2].split(':')[0]
                if p_id.startswith('p1'):
                    p_id = 'p1'
                elif p_id.startswith('p2'):
                    p_id = 'p2'
                species = parts[2].split(':', 1)[1].strip() if ':' in parts[2] else ''
                if p_id in z_move_users and species:
                    z_move_users[p_id].append(species)

            elif parts[1] == 'win' and len(parts) > 2:
                win_player = parts[2].lower()


        # (debug print removed)

        # Build MatchScout objects only for players that match the requested targets
        scouts: List[MatchScout] = []
        for p_id, player_name in players.items():
            if player_name in self.targets:
                roster: List[Pokemon] = []
                for species in teams_raw.get(p_id, []):
                    is_mega = species in megas.get(p_id, set())
                    
                    # Check if Greninja should be Greninja-Ash
                    if species == 'Greninja' and greninja_behavior[p_id]['used_move'] and not greninja_behavior[p_id]['showed_protean']:
                        species = 'Greninja-Ash'
                    
                    # Prefer a recorded mega variant name when available (e.g. Charizard-Mega-Y).
                    variant_name = megas_variant_map.get(p_id, {}).get(species)
                    if not variant_name and '-' in species:
                        base_species = species.split('-', 1)[0]
                        variant_name = megas_variant_map.get(p_id, {}).get(base_species)
                    final_species = variant_name if variant_name else species
                    if not is_mega and 'Mega' in final_species:
                        is_mega = True
                    types = self._lookup_types(final_species)
                    roster.append(Pokemon(final_species, types, is_mega))

                if not any(mon.is_mega for mon in roster):
                    self._assume_mega_if_unrevealed(roster)

                # The opponent is the other player slot for this match.
                opponent_id = 'p2' if p_id == 'p1' else 'p1'
                opponent = players.get(opponent_id, 'unknown')
                # W/L is inferred only if there is a win line in the log.
                result = 'W' if win_player == player_name else 'L' if win_player else '?'
                z_move_user = ', '.join(z_move_users.get(p_id, []))

                scouts.append(
                    MatchScout(
                        player=player_name,
                        opponent=opponent,
                        tour=tour_name,
                        result=result,
                        z_move_user=z_move_user,
                        team=Team(player=player_name, roster=roster),
                    )
                )

        return scouts

    def _lookup_types(self, species: str) -> List[str]:
        if species in self.dex_config:
            return self.dex_config[species].get('types', [])

        if species.endswith('-*'):
            base = species[:-2]
            # Treat all Urshifu-* entries as Urshifu-Rapid-Strike for type resolution.
            if base == 'Urshifu':
                rapid_strike = 'Urshifu-Rapid-Strike'
                if rapid_strike in self.dex_config:
                    return self.dex_config[rapid_strike].get('types', [])
            if base in self.dex_config:
                return self.dex_config[base].get('types', [])

        if '-' in species:
            base = species.split('-', 1)[0]
            if base in self.dex_config:
                return self.dex_config[base].get('types', [])

        return []

    def _assume_mega_if_unrevealed(self, roster: List[Pokemon]) -> None:
        mega_candidates = [mon for mon in roster if self._can_mega_evolve(mon.species)]
        if not mega_candidates:
            return

        if len(mega_candidates) == 1:
            mega_candidates[0].is_mega = True
            return

        priority = {
            'Garchomp': 0,
            'Tyranitar': 1,
        }
        candidate = mega_candidates[0]
        for mon in mega_candidates[1:]:
            current_priority = priority.get(candidate.species, 2)
            next_priority = priority.get(mon.species, 2)
            if next_priority > current_priority:
                candidate = mon
        candidate.is_mega = True

    def _can_mega_evolve(self, species: str) -> bool:
        base = species.split('-', 1)[0]
        for name in self.dex_config:
            if name.startswith(f"{base}-Mega"):
                return True
        return False
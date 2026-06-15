import requests
from typing import Dict, List, Optional

from src.models import Pokemon, Team

class ShowdownParser:
    def __init__(self, target_usernames: List[str], dex_config: Dict[str, Dict[str, List[str]]]):
        self.targets = [username.lower() for username in target_usernames]
        self.dex_config = dex_config

    def parse_replay(self, replay_url: str) -> List[Team]:
        log_url = replay_url if replay_url.endswith('.log') else f"{replay_url}.log"
        response = requests.get(log_url)
        response.raise_for_status()
        log_lines = response.text.splitlines()

        # players: maps p1/p2 -> username (lowercased)
        players: Dict[str, str] = {}
        # teams_raw: temporary list of species strings from team preview for p1/p2
        teams_raw: Dict[str, List[str]] = {'p1': [], 'p2': []}
        # megas: set of species that mega-evolved during the battle for p1/p2
        megas: Dict[str, set] = {'p1': set(), 'p2': set()}

        for line in log_lines:
            parts = line.split('|')
            if len(parts) < 2:
                continue

            # Example: "|player|p1|Yelodash|..." -> capture mapping p1 -> 'yelodash'
            if parts[1] == 'player' and len(parts) > 3:
                p_id, p_name = parts[2], parts[3].lower()
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
                # normalize p1a/p1b -> p1, p2a -> p2
                if p_id.startswith('p1'):
                    p_id = 'p1'
                elif p_id.startswith('p2'):
                    p_id = 'p2'
                species_who_megaed = parts[3].strip()
                if p_id in megas:
                    megas[p_id].add(species_who_megaed)

        # Build Team objects only for players that match the requested targets
        scouts: List[Team] = []
        for p_id, player_name in players.items():
            if player_name in self.targets:
                roster: List[Pokemon] = []
                # Preserve preview order; mark is_mega if species appeared in megas set
                for species in teams_raw.get(p_id, []):
                    is_mega = species in megas.get(p_id, set())
                    types = self.dex_config.get(species, {}).get('types', [])
                    roster.append(Pokemon(species, types, is_mega))
                scouts.append(Team(player=player_name, roster=roster))

        return scouts
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

        players: Dict[str, str] = {}
        teams_raw: Dict[str, List[str]] = {'p1': [], 'p2': []}
        megas: Dict[str, set] = {'p1': set(), 'p2': set()}

        for line in log_lines:
            parts = line.split('|')
            if len(parts) < 2:
                continue

            if parts[1] == 'player' and len(parts) > 3:
                p_id, p_name = parts[2], parts[3].lower()
                players[p_id] = p_name

            elif parts[1] == 'poke' and len(parts) > 3:
                p_id = parts[2]
                species = parts[3].split(',')[0].strip()
                if p_id in teams_raw:
                    teams_raw[p_id].append(species)

            elif parts[1] == '-mega' and len(parts) > 3:
                p_id = parts[2].split(':')[0]
                if p_id.startswith('p1'):
                    p_id = 'p1'
                elif p_id.startswith('p2'):
                    p_id = 'p2'
                species_who_megaed = parts[3].strip()
                if p_id in megas:
                    megas[p_id].add(species_who_megaed)

        scouts: List[Team] = []
        for p_id, player_name in players.items():
            if player_name in self.targets:
                roster: List[Pokemon] = []
                for species in teams_raw.get(p_id, []):
                    is_mega = species in megas.get(p_id, set())
                    types = self.dex_config.get(species, {}).get('types', [])
                    roster.append(Pokemon(species, types, is_mega))
                scouts.append(Team(player=player_name, roster=roster))

        return scouts

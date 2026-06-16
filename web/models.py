from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Tour:
    name: str
    replays: List[str]

@dataclass
class ScoutRequest:
    usernames: List[str]
    tier: str
    tours: List[Tour]
    
    @staticmethod
    def from_json(data: dict) -> 'ScoutRequest':
        """Parse JSON data from web form into ScoutRequest object."""
        usernames_str = data.get('usernames', '').strip()
        if not usernames_str:
            raise ValueError("Usernames are required")
        
        usernames = [u.strip().lower() for u in usernames_str.replace(',', ' ').split() if u.strip()]
        
        tier = data.get('tier', '').strip()
        if not tier:
            raise ValueError("Tier is required")
        
        tours_data = data.get('tours', [])
        if not tours_data:
            raise ValueError("At least one tour is required")
        
        tours = []
        for tour_data in tours_data:
            name = tour_data.get('name', '').strip()
            replays_str = tour_data.get('replays', '').strip()
            
            if not name:
                raise ValueError("Tour name is required")
            if not replays_str:
                raise ValueError(f"At least one replay URL is required for tour '{name}'")
            
            # Split replays by newline and filter empty lines
            replays = [url.strip() for url in replays_str.split('\n') if url.strip()]
            tours.append(Tour(name=name, replays=replays))
        
        return ScoutRequest(usernames=usernames, tier=tier, tours=tours)

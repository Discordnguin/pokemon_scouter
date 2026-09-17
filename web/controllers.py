from config.gen7ou_dex import GEN7_OU_DEX
from src.parser import ShowdownParser
from src.sorter import TeamSorter, Gen7Strategy, Gen8Strategy
from web.models import ScoutRequest

class ScoutController:
    """Controller for managing scout generation logic."""
    
    def generate_scouts(self, request: ScoutRequest) -> dict:
        """
        Generate scout output from a ScoutRequest.
        
        Args:
            request: ScoutRequest containing usernames, tier, and tours
            
        Returns:
            Dictionary containing 'raw_text' importable and 'teams' list for visuals
        """
        parser = ShowdownParser(target_usernames=request.usernames, dex_config=GEN7_OU_DEX)
        scouts = []
        
        for tour in request.tours:
            for replay_url in tour.replays:
                scouts.extend(parser.parse_replay(replay_url, tour_name=tour.name))
        
        if not scouts:
            raise ValueError("No matching scouts found. Check usernames and replay URLs.")
        
        tier_lower = request.tier.lower()
        if tier_lower in ['gen6ou', 'gen7ou']:
            strategy = Gen7Strategy()
        else:
            strategy = Gen8Strategy()
        
        output_lines: list[str] = []
        structured_teams = []
        
        for match in scouts:
            # 1. Format Header
            header_text = f"[{request.tier}] {match.tour} vs {match.opponent} ({match.result})"
            if match.z_move_user:
                header_text += f" Z: {match.z_move_user}"
            
            output_lines.append(f"=== {header_text} ===")
            
            # 2. Sort Team
            sorter = TeamSorter(match.team, strategy)
            ordered_team = sorter.sort_scout()
            
            # 3. Save for visual frontend
            structured_teams.append({
                "header": header_text,
                "mons": ordered_team
            })
            
            # 4. Save for raw importable
            for mon in ordered_team:
                output_lines.append(mon)
                output_lines.append("") # preserving your double-spacing format
        
        return {
            "raw_text": "\n".join(output_lines).rstrip() + "\n",
            "teams": structured_teams
        }
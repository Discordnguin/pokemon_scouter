from config.gen7ou_dex import GEN7_OU_DEX
from src.parser import ShowdownParser
from src.sorter import TeamSorter, Gen7Strategy, Gen8Strategy
from web.models import ScoutRequest

class ScoutController:
    """Controller for managing scout generation logic."""
    
    def generate_scouts(self, request: ScoutRequest) -> str:
        """
        Generate scout output from a ScoutRequest.
        
        Args:
            request: ScoutRequest containing usernames, tier, and tours
            
        Returns:
            Formatted scout output as a string
        """
        parser = ShowdownParser(target_usernames=request.usernames, dex_config=GEN7_OU_DEX)
        scouts = []
        
        # Parse all replays from all tours
        for tour in request.tours:
            for replay_url in tour.replays:
                scouts.extend(parser.parse_replay(replay_url, tour_name=tour.name))
        
        if not scouts:
            raise ValueError("No matching scouts found. Check usernames and replay URLs.")
        
        # Select strategy based on tier
        tier_lower = request.tier.lower()
        if tier_lower in ['gen6ou', 'gen7ou']:
            strategy = Gen7Strategy()
        else:
            strategy = Gen8Strategy()
        
        # Generate output
        output_lines: list[str] = []
        
        for match in scouts:
            header = f"=== [{request.tier}] {match.tour} vs {match.opponent} ({match.result})"
            if match.z_move_user:
                header += f" Z: {match.z_move_user}"
            header = f"{header} ==="
            output_lines.append(header)
            
            sorter = TeamSorter(match.team, strategy)
            ordered_team = sorter.sort_scout()
            for mon in ordered_team:
                output_lines.append(mon)
                output_lines.append("")
        
        return "\n".join(output_lines).rstrip() + "\n"

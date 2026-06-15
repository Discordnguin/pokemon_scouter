from config.gen7ou_dex import GEN7_OU_DEX # Or reading the JSON
from src.parser import ShowdownParser
from src.sorter import TeamSorter

def main():
    targets = ["yelodash"]
    replay = "https://replay.pokemonshowdown.com/smogtours-gen7ou-946180"
    
    # 1. Parse the raw log data
    parser = ShowdownParser(target_usernames=targets, dex_config=GEN7_OU_DEX)
    scouts = parser.parse_replay(replay)
    
    # 2. Sort and apply heuristics to found teams
    for team in scouts:
        sorter = TeamSorter(team)
        ordered_team = sorter.sort_scout()
        
        print(f"--- Scout for {team.player} ---")
        print("\n".join(ordered_team))

if __name__ == "__main__":
    main()
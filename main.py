from collections import defaultdict

from config.gen7ou_dex import GEN7_OU_DEX # Or reading the JSON
from src.parser import ShowdownParser
from src.sorter import TeamSorter

def main():
    targets = ["yelodash"]
    replays_by_tour = {
        "WCoP": [
            "https://replay.pokemonshowdown.com/smogtours-gen7ou-946180",
            "https://replay.pokemonshowdown.com/smogtours-gen7ou-944682",
            "https://replay.pokemonshowdown.com/smogtours-gen7ou-944254",
            "https://replay.pokemonshowdown.com/smogtours-gen7ou-940466",
            "https://replay.pokemonshowdown.com/smogtours-gen7ou-930702",
            "https://replay.pokemonshowdown.com/smogtours-gen7ou-931174",
        ],
    }

    # User-specified tier to include in the header (e.g. 'gen7ou')
    tier = "gen7ou"

    parser = ShowdownParser(target_usernames=targets, dex_config=GEN7_OU_DEX)
    scouts = []
    for tour_name, replay_urls in replays_by_tour.items():
        for replay_url in replay_urls:
            scouts.extend(parser.parse_replay(replay_url, tour_name=tour_name))

    output_lines: list[str] = []
    # Emit one header per team: "=== {tour} vs {opponent} ({result}) Z: {z} ==="
    for match in scouts:
        header = f"=== [{tier}] {match.tour} vs {match.opponent} ({match.result})"
        if match.z_move_user:
            header += f" Z: {match.z_move_user}"
        header = f"{header} ==="
        output_lines.append(header)

        sorter = TeamSorter(match.team)
        ordered_team = sorter.sort_scout()
        # Print each Pokemon on its own line, followed by an empty line
        for mon in ordered_team:
            output_lines.append(mon)
            output_lines.append("")

    # Write output to file
    out_path = "scouts_output.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    # Also print to stdout for convenience
    print(open(out_path, encoding="utf-8").read())

if __name__ == "__main__":
    main()
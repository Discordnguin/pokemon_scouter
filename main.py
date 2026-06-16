import sys
from config.gen7ou_dex import GEN7_OU_DEX
from src.parser import ShowdownParser
from src.sorter import TeamSorter, Gen6Strategy, Gen7Strategy, Gen8Strategy

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "input.txt"
OUTPUT_FILE = "scouts_output.txt"

def parse_input_file(path: str) -> tuple[list[str], str, dict[str, list[str]]]:
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [line.rstrip() for line in f.readlines()]

    lines = [line for line in raw_lines if line.strip() and not line.strip().startswith("#")]
    if len(lines) < 2:
        raise ValueError("input.txt must contain at least a target line and a tier line.")

    targets = [target.strip().lower() for target in lines[0].replace(",", " ").split() if target.strip()]
    tier = lines[1].strip()

    replays_by_tour: dict[str, list[str]] = {}
    current_tour: str | None = None
    for line in lines[2:]:
        clean = line.strip()
        if clean.lower().startswith("http://") or clean.lower().startswith("https://"):
            if current_tour is None:
                raise ValueError("Replay URL found before a tour name in input.txt.")
            replays_by_tour[current_tour].append(clean)
            continue

        current_tour = clean
        replays_by_tour[current_tour] = []

    return targets, tier, replays_by_tour


def main():
    targets, tier, replays_by_tour = parse_input_file(INPUT_FILE)

    parser = ShowdownParser(target_usernames=targets, dex_config=GEN7_OU_DEX)
    scouts = []
    for tour_name, replay_urls in replays_by_tour.items():
        for replay_url in replay_urls:
            scouts.extend(parser.parse_replay(replay_url, tour_name=tour_name))

    output_lines: list[str] = []
    tier_lower = tier.lower()
    if tier_lower == 'gen6ou':
        strategy = Gen6Strategy()
    elif tier_lower == 'gen7ou':
        strategy = Gen7Strategy()
    else:
        strategy = Gen8Strategy()

    for match in scouts:
        header = f"=== [{tier}] {match.tour} vs {match.opponent} ({match.result})"
        if match.z_move_user:
            header += f" Z: {match.z_move_user}"
        header = f"{header} ==="
        output_lines.append(header)

        sorter = TeamSorter(match.team, strategy)
        ordered_team = sorter.sort_scout()
        for mon in ordered_team:
            output_lines.append(mon)
            output_lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines).rstrip() + "\n")

    with open(OUTPUT_FILE, encoding="utf-8") as f:
        sys.stdout.write(f.read())

if __name__ == "__main__":
    main()
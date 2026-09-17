# Pokémon Showdown Scout Generator

A tool to generate tier-optimized team scouts from Pokémon Showdown replay logs.

## Quick Start

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
# or on Mac/Linux:
# source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

#### Option A: Command Line (Batch Mode)

Create an `input.txt` file:
```
zryan74 other-username
gen7ou
Tournament Name 1
https://replay.pokemonshowdown.com/smogtours-gen7ou-936926
https://replay.pokemonshowdown.com/smogtours-gen7ou-939819
Another Tournament
https://replay.pokemonshowdown.com/smogtours-gen7ou-946741
```

Then run:
```bash
python main.py
```

Output will be written to `scouts_output.txt`.

**Input Format:**
- Line 1: Username(s) - separated by spaces or commas. Non-alphanumeric characters are ignored (e.g., `z-ryan74` matches replay user `zryan74`)
- Line 2: Tier (e.g., `gen7ou`, `gen8ou`, `gen6ou`)
- Lines 3+: Tournament names and replay URLs (group URLs under the tournament name above them)

#### Option B: Web UI

```bash
python web_app.py
```

Then open: `http://localhost:5000`

- Enter username(s)
- Select tier
- Add tournament names and replay URLs
- Click "Generate Scout"
- Copy to clipboard or download as text file

## Features

- **Multi-format support**: Gen6OU, Gen7OU, Gen8OU with tier-specific sorting strategies
- **Mega Evolution**: Preserves Mega variants (e.g., `Charizard-Mega-Y`)
- **Z-Move tracking**: Shows which Pokémon used Z-Moves
- **Flexible username matching**: Handles spaces, dashes, special characters (`z-ryan74` = `zryan74` = `z ryan74`)
- **Web UI**: Real-time team generation with copy/download

## Project Structure

```
.
├── main.py                 # CLI entry point
├── web_app.py             # Flask web server
├── requirements.txt       # Python dependencies
├── config/
│   ├── __init__.py
│   └── gen7ou_dex.json    # Pokédex data for Gen7OU
├── src/
│   ├── __init__.py
│   ├── models.py          # Data models (Pokémon, Team, MatchScout)
│   ├── parser.py          # Showdown replay parser
│   └── sorter.py          # Tier-specific sorting strategies
└── web/
    ├── models.py          # Web request models
    ├── controllers.py     # Request handlers
    └── templates/
        └── index.html     # Web UI
```

## Configuration

Edit `config/gen7ou_dex.json` to customize Pokédex entries, types, and Mega forms.

## Troubleshooting

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Port 5000 already in use:**
```bash
python -c "import socket; s=socket.socket(); s.bind(('',5000)); print('Port available')"
# If busy, modify web_app.py to use a different port:
# app.run(debug=True, port=5001)
```

**Username not matching:**
- Ensure username in `input.txt` normalizes to the same alphanumeric string as the replay
- Example: `z-ryan74` will match replay user `zryan74` ✓

## Development

To add debug output for sorting decisions:
- CLI: Output includes `[DEBUG]` lines from sorting logic
- Web: Check browser console for debug information

Modify `src/sorter.py` to adjust tier-specific sorting strategies or add new tiers.

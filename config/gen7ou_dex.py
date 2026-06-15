import json
from pathlib import Path
from typing import Dict, Any

PACKAGE_DIR = Path(__file__).resolve().parent

with open(PACKAGE_DIR / "gen7ou_dex.json", encoding="utf-8") as f:
    GEN7_OU_DEX: Dict[str, Dict[str, Any]] = json.load(f)

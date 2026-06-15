#!/usr/bin/env python3
import re, json, requests, sys
URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/pokedex.ts"
r = requests.get(URL)
r.raise_for_status()
text = r.text

# find all occurrences of 'name: "Species"' and their positions
name_re = re.compile(r'name\s*:\s*"([^"]+)"')
types_re = re.compile(r'types\s*:\s*\[\s*([^\]]*?)\s*\]', re.S)

names = list(name_re.finditer(text))
dex = {}
for i, m in enumerate(names):
    name = m.group(1)
    start = m.end()
    end = names[i+1].start() if i+1 < len(names) else len(text)
    block = text[start:end]
    types_match = types_re.search(block)
    if types_match:
        raw = types_match.group(1)
        # extract quoted strings inside the array
        types = re.findall(r'"([^"]+)"', raw)
    else:
        types = []
    dex[name] = {"types": types}

out_path = "config/gen7ou_dex.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(dex, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(dex)} entries to {out_path}")
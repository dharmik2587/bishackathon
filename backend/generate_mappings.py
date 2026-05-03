#!/usr/bin/env python3
"""
generate_mappings.py
Scans your standards_enriched.json and prints suggested DIRECT_MAPPINGS
entries for any standard whose title contains strong domain keywords.
Run this once, review output, paste into inference.py DIRECT_MAPPINGS.

Usage:
    python generate_mappings.py --standards ../frontend/public/standards_enriched.json
"""

import json, re, argparse, sys
from pathlib import Path

# Keywords that make a title a good direct-mapping candidate
STRONG_SIGNALS = [
    "cement", "concrete", "aggregate", "brick", "block", "pipe", "tile",
    "steel", "aluminium", "aluminum", "glass", "gypsum", "lime", "timber",
    "plywood", "bitumen", "cable", "wire", "valve", "fitting", "sanitary",
    "door", "window", "shutter", "waterproof", "roofing", "flooring",
    "insulation", "adhesive", "sealant", "paint", "mortar", "reinforcement",
    "deformed", "bar", "rod", "section", "sheet", "board", "panel", "fibre",
    "prestressed", "precast", "hollow", "solid", "aerated", "fly ash",
    "slag", "pozzolana", "pozzolanic", "sulphate", "supersulphated", "white",
    "rapid hardening", "oil well", "masonry", "asbestos", "corrugated",
]

def clean_title(title: str) -> str:
    # lowercase, remove spec jargon words that add noise
    t = title.lower().strip()
    noise = [
        r'\bspecification for\b', r'\bspecification\b', r'\bstandard\b',
        r'\brequirements? for\b', r'\brequirements?\b', r'\bfor general\b',
        r'\bpart \d+\b', r'\b\(\d+\)\b', r'\bcode of practice\b',
        r'\bmethods? of test\b', r'\bmethods?\b',
    ]
    for n in noise:
        t = re.sub(n, '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s+', ' ', t).strip(' :-,.')
    return t

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--standards', required=True)
    parser.add_argument('--min_len', type=int, default=8, help='Minimum key length to emit')
    args = parser.parse_args()

    if not Path(args.standards).exists():
        print(f"File not found: {args.standards}"); sys.exit(1)

    with open(args.standards, 'r', encoding='utf-8') as f:
        standards = json.load(f)

    print(f"# Auto-generated DIRECT_MAPPINGS entries ({len(standards)} standards scanned)")
    print(f"# Paste relevant ones into DIRECT_MAPPINGS in inference.py\n")

    emitted = 0
    for s in sorted(standards, key=lambda x: x.get('standardNumber', '')):
        num = s.get('standardNumber', '').strip()
        title = s.get('title', '').strip()
        if not num or not title:
            continue

        title_lower = title.lower()
        if not any(sig in title_lower for sig in STRONG_SIGNALS):
            continue

        key = clean_title(title)
        if len(key) < args.min_len:
            continue

        # Also emit shortened variant (first 3-5 meaningful words)
        words = key.split()
        short_key = ' '.join(words[:5]) if len(words) > 5 else key

        print(f'    "{key}": "{num}",')
        if short_key != key:
            print(f'    "{short_key}": "{num}",')
        emitted += 1

    print(f"\n# Total: {emitted} entries generated")

if __name__ == '__main__':
    main()
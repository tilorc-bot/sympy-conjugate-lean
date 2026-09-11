#!/usr/bin/env python3
"""Reject unfinished proofs and unexpected assumptions in the certified theorem closure."""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
for path in [root / 'LeanIdea.lean', *sorted((root / 'LeanIdea').rglob('*.lean'))]:
    if re.search(r'\b(sorry|admit|axiom)\b', path.read_text()):
        raise SystemExit(f'Unfinished proof or axiom declaration: {path}')
result = subprocess.run(['lake', 'env', 'lean', '-DwarningAsError=true', 'scripts/Audit.lean'],
                        cwd=root, text=True, capture_output=True, check=True)
print(result.stdout, end='')
entries = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", result.stdout, re.S)
if len(entries) != 10:
    raise SystemExit('Unexpected axiom audit output')
for name, assumptions in entries:
    unexpected = set(filter(None, re.split(r'[,\s]+', assumptions))) - {'propext', 'Classical.choice', 'Quot.sound'}
    if unexpected:
        raise SystemExit(f'{name}: unexpected axioms {unexpected}')

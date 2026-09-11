#!/usr/bin/env python3
"""Source drift check, NOT a proof of Python/Lean correspondence."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check(checkout=None):
    spec = json.loads((ROOT / 'spec/rules.json').read_text())
    snapshot = ROOT / 'spec/source'
    roots = [snapshot]
    if checkout is not None:
        head = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if head != spec['commit']:
            raise ValueError(f"HEAD {head} != {spec['commit']}")
        roots.append(checkout)
    for root in roots:
        for name, digest in spec['files'].items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f'changed source: {root / name}')
        handler = spec['handler']
        data = (root / handler['path']).read_bytes()
        node = next(n for n in ast.parse(data).body
                    if isinstance(n, ast.FunctionDef) and n.name == handler['name'])
        extracted = b''.join(data.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])
        if (node.lineno, node.end_lineno) != (handler['start'], handler['end']):
            raise ValueError('handler line range changed')
        if hashlib.sha256(extracted).hexdigest() != handler['sha256']:
            raise ValueError('handler digest changed')
        if extracted != (snapshot / 'refine_conjugate.py').read_bytes():
            raise ValueError('handler snapshot differs')
    if {r['id'] for r in spec['rules']} != {
        'conjugate.real', 'conjugate.imaginary', 'conjugate.log.off_cut'
    } or len(spec['rules']) != 3:
        raise ValueError('selected rule set changed')
    for rule in spec['rules']:
        if rule['commit'] != spec['commit']:
            raise ValueError('inconsistent rule commit')
    print('Source drift check passed (not a correspondence proof).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', nargs='?', type=Path, help='frozen SymPy git checkout; omit to check bundled snapshot')
    args = parser.parse_args()
    try:
        check(args.checkout)
    except (ValueError, OSError, subprocess.CalledProcessError, StopIteration) as exc:
        parser.exit(1, f'Drift check failed: {exc}\nReview changed branches and update target, snapshots, digests, and proof mapping together.\n')

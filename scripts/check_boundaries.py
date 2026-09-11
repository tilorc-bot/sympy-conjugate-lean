#!/usr/bin/env python3
"""Integration checks at the frozen checkout; tracing separates handler branches from simplification."""
import json
from pathlib import Path
import sys
from check_spec import check

checkout = Path(sys.argv[1]).resolve()
check(checkout)
sys.path.insert(0, str(checkout))
from sympy import I, Q, S, Symbol, ask, conjugate, log, oo, refine, zoo, nan
from sympy.assumptions.refine import refine_conjugate

x = Symbol('x')
assert refine(conjugate(x), Q.real(x)) == x
assert refine(conjugate(x), Q.imaginary(x)) == -x
assert refine(conjugate(log(x)), Q.complex(x) & ~Q.nonpositive(x)) == log(conjugate(x))
assert refine(conjugate(log(x)), Q.complex(x)) == conjugate(log(x))
# Compound arguments require predicates on the whole expression.
f = x ** Symbol('n')
assert refine(conjugate(f), Q.real(f)) == f
assert refine(conjugate(f), Q.imaginary(f)) == -f

cases = [(S(2), True, False, True), (S(-2), True, False, False),
         (S.Zero, True, False, False), (I, False, True, True),
         (-2*I, False, True, True), (1+I, False, False, True),
         (oo, False, False, False), (zoo, False, False, False),
         (nan, None, None, False)]
rows = []
for z, real, imaginary, off_cut in cases:
    actual_real, actual_imag = ask(Q.real(z)), ask(Q.imaginary(z))
    guard = ask(~Q.nonpositive(z)) is True and ask(Q.complex(z)) is True
    assert (actual_real, actual_imag, guard) == (real, imaginary, off_cut), (z, actual_real, actual_imag, guard)
    visited = set()
    def trace(frame, event, arg):
        if frame.f_code is refine_conjugate.__code__ and event == 'line':
            visited.add(frame.f_lineno)
        return trace
    expr = conjugate(log(z, evaluate=False), evaluate=False)
    sys.settrace(trace)
    try:
        output = refine_conjugate(expr, True)
    finally:
        sys.settrace(None)
    fired = 616 in visited
    assert fired == guard, (z, visited)
    if guard:
        assert output == log(conjugate(z))
    rows.append(dict(value=str(z), real=actual_real, imaginary=actual_imag,
                     complex=ask(Q.complex(z)), log_guard=guard,
                     log_branch_fired=fired, handler_output=str(output),
                     ordinary_refine=str(refine(conjugate(log(z))))))
print(json.dumps(rows, indent=2))

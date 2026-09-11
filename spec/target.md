# Frozen Python target and trusted contract

Target: SymPy PR [#29173](https://github.com/sympy/sympy/pull/29173), head inspected
2026-09-11, **3bc91a30609223ca4e7da1a6feaf62bc179a6f7e**, version **1.15.0.dev**.
The PR description is not the specification; the source at this commit is.

## Branch correspondence

The handler is [`refine_conjugate`, lines 569–677](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L569).
Its [dispatch registration is line 694](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L694).

| Rule | Input | Successful guard | Replacement | Source |
| --- | --- | --- | --- | --- |
| `conjugate.real` | `conjugate(x)` | `ask(Q.real(x), A)` | `x` | [672–673](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L672) |
| `conjugate.imaginary` | `conjugate(x)` | `ask(Q.imaginary(x), A)` | `-x` | [675–676](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L675) |
| `conjugate.log.off_cut` | `conjugate(log(x))` | `ask(~Q.nonpositive(x), A)` then `ask(Q.complex(x), A)` | `log(conjugate(x))` | [612–616](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L612) |

Here “successful” means True, not None or False. The log code performs two
short-circuited queries, not one query of a conjunction. Their mathematical
contract is the conjunction shown in the plan.

Actual order and reachability:

1. Log handling comes first. Off-cut success returns immediately. Otherwise a
   positive negative-real query returns `log(x) - 2*I*pi`. If neither returns,
   execution can reach the generic tests.
2. A Pow argument with a positively real exponent enters lines 620–629 and
   always returns: integer-exponent/complex-base, negative-real square-root,
   nonnegative-cut/complex-base cases, or unchanged expression. The integer
   query here does not receive `assumptions`. These branches are outside scope.
3. Each inverse-trigonometric group (`asin/acos`, `acot/atan`, `asec/acsc`)
   always returns when its pattern matches, including an unchanged return
   when its tests are inconclusive. These branches are outside scope.
4. The real branch follows all those blocks. The imaginary branch is an
   `elif`, reached only when the real query is not True. The final fallback
   returns the original expression.

Before dispatch, [`refine` lines 59–84](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L59)
recursively refines children, reconstructs the expression (which can evaluate),
and tries `_eval_refine`, which can return early. Construction of `conjugate`
and `log` can also evaluate before `refine` is called. We certify the selected
branch denotations when reached, not that each input necessarily reaches them.

## Mathematical predicates and trusted contracts

At an admitted finite value `z : ℂ`, `Q.real` means `z.im = 0`, `Q.imaginary`
means `z.re = 0 ∧ z ≠ 0`, and `Q.nonpositive` means
`z.im = 0 ∧ z.re ≤ 0`. `Q.complex` supplies admission into this finite domain.
See the frozen [real definition](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/predicates/sets.py#L123),
[complex definition](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/predicates/sets.py#L262),
and [imaginary definition](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/predicates/sets.py#L298).
Imaginary excludes zero. Its interpretation implies the weaker zero-real-part
hypothesis sufficient for the elementary theorem; the converse fails at zero.

Application to Python trusts these distinct claims:

1. For valuations satisfying `A`, a successful `ask(P, A)` entails the stated
   mathematical interpretation of `P`, including queried Boolean negation.
   `sound_of_successful_ask` takes the corresponding implication explicitly.
2. A positive `Q.real`, `Q.imaginary`, or `Q.complex` on the relevant expression
   supplies its finite complex value. In the generic rules this is the **entire
   argument of conjugate**, even if compound; finite variables do not suffice
   for expressions such as `1/x` or `log(x)`. Bare predicate negations do not
   supply finiteness. For the log rule `x` is the inner log argument.
3. At admitted values, Python conjugation, negation, and principal logarithm
   denote the Lean operations. The log guard excludes zero and is preserved by
   conjugation, so both logarithms are ordinary principal logarithms.
4. The recorded source branches correspond to the three entries in the small
   rule model. This is manual source review, not a verified Python translator.

Lean checks the identities, guard implications, zero exclusion, conjugation
preservation, and selected-rule soundness. It does not check `ask`, Python's
execution semantics, the above operation correspondence, or all of `refine`.
There are no project correctness axioms. The final theorem's finite input is
explicit in its `z : ℂ` binder. A source digest detects drift; it does not prove
any of these trusted claims.

Lean totalizes logarithm at zero; SymPy has `log(0) = zoo`. We exclude zero
regardless of whether an algebraic Lean equality holds there. `oo`, `zoo`,
`nan`, general powers, negative-real logs, square roots, inverse trigonometric
functions, and the rest of the PR are outside the certified scope. The older
real-power example remains an explicitly uncertified example.

## Validation

[Upstream test at lines 328–370](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/tests/test_refine.py#L328):
`python -m pytest sympy/assumptions/tests/test_refine.py -k conjugate -q`.
Python 3.12.14 and dependencies in [requirements.txt](../scripts/requirements.txt).
The exact frozen test fails at line 352 with `NameError: asin is not defined`,
after its elementary and logarithm assertions have passed. See
[original output](results/upstream-test.txt). No target source was modified.
The [separate test-import patch](patches/test-imports.patch) adds the missing
inverse-trig imports; running a temporary copy with only that patch gives
**1 passed, 19 deselected** ([output](results/repaired-test.txt)). This is a
validation convenience, not a new certified target. CI runs our selected
integration checks on the unmodified target, not the broken upstream test.

[Boundary checks](../scripts/check_boundaries.py) assert symbolic rules and
compound-argument assumptions, then inspect 2, -2, 0, I, -2I, 1+I, oo, zoo, nan.
They query guards separately, keep input construction unevaluated for direct
handler calls, and trace the off-cut return line to distinguish branch firing
from ordinary evaluation. [Recorded output](results/boundaries.txt) shows the
log guard rejects zero, negative reals, and exceptional values; `nan` queries
are unknown. Ordinary `refine(log(oo).conjugate())` can still simplify elsewhere.
These finite samples test integration assumptions; they are not proofs.

The [manifest](rules.json) records SHA-256 digests of full context files and the
exact handler bytes, with extraction instructions. The drift checker compares
both the supplied checkout's HEAD and its actual file contents, as well as the
bundled snapshot. Any mismatch requires reviewing the branches and mapping.
The copied source retains the [SymPy BSD license](source/LICENSE); original
project code and prose are MIT licensed.

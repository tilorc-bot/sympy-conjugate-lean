# SymPy conjugation rules, checked in Lean

This pilot proves that **three selected rewrite branches** in SymPy PR #29173
preserve their mathematical meaning at finite complex values under explicit
guards: conjugation of real values, imaginary values, and principal logarithms
off the nonpositive real ray. Lean checks the identities and guard bridges.
Applying them to Python trusts the assumptions engine, finite-value admission,
operation semantics, and manually reviewed source correspondence. This is not
a proof of the whole PR or of SymPy's assumptions engine.

| Selected Python branch (frozen commit) | Lean theorem |
| --- | --- |
| [`Q.real(x)` → `x`](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L672) | [`real_guard`](https://github.com/tilorc-bot/sympy-conjugate-lean/blob/e8f450009d7d5d2d56ec906f2cc0a4e541640053/LeanIdea/Conjugate/Guards.lean) |
| [`Q.imaginary(x)` → `-x`](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L675) | [`imaginary_guard`](https://github.com/tilorc-bot/sympy-conjugate-lean/blob/e8f450009d7d5d2d56ec906f2cc0a4e541640053/LeanIdea/Conjugate/Guards.lean) |
| [`~Q.nonpositive(x)` and `Q.complex(x)` → `log(conjugate(x))`](https://github.com/sympy/sympy/blob/3bc91a30609223ca4e7da1a6feaf62bc179a6f7e/sympy/assumptions/refine.py#L612) | [`conjugate_log_off_cut`](https://github.com/tilorc-bot/sympy-conjugate-lean/blob/e8f450009d7d5d2d56ec906f2cc0a4e541640053/LeanIdea/Conjugate/Log.lean) |

For $z\in\mathbb C$:

$$\mathrm{Im}(z)=0\implies\overline z=z,$$

$$\mathrm{Re}(z)=0\implies\overline z=-z,$$

$$z\notin(-\infty,0]\implies\overline{\mathrm{Log}(z)}=\mathrm{Log}(\overline z).$$

SymPy's imaginary guard additionally excludes zero; the identity safely uses
its weaker consequence. The log guard excludes zero on both sides.
[`selected_rule_sound`](https://github.com/tilorc-bot/sympy-conjugate-lean/blob/e8f450009d7d5d2d56ec906f2cc0a4e541640053/LeanIdea/Conjugate/Soundness.lean) packages all three
rules. `sound_of_successful_ask` takes guard correctness as a hypothesis.

[![Proofs](https://github.com/tilorc-bot/sympy-conjugate-lean/actions/workflows/lean.yml/badge.svg)](https://github.com/tilorc-bot/sympy-conjugate-lean/actions/workflows/lean.yml)

With [elan](https://github.com/leanprover/elan) installed:

```bash
git clone https://github.com/tilorc-bot/sympy-conjugate-lean.git
cd sympy-conjugate-lean
lake exe cache get Mathlib.Analysis.SpecialFunctions.Pow.Complex
lake build
python3 scripts/check_axioms.py
python3 scripts/check_spec.py
```

Pinned Lean **v4.33.1**, mathlib **v4.33.1** at
`0df444a360eaa60ab8c11dca51a86af692955474`, with all transitive commits in
[lake-manifest.json](lake-manifest.json). CI installs elan **v4.2.4** using a
SHA-256-checked release and pins third-party actions to commit SHAs. It uses
`lake build`, never an unpinned dependency update. Every proof module is in the
default target; warnings are errors. The axiom audit allows only `propext`,
`Classical.choice`, and `Quot.sound` and rejects unfinished proofs.

Reproduce the Python source check and integration checks with Python **3.12.14**:

```bash
git init /tmp/sympy-target
git -C /tmp/sympy-target fetch --depth 1 https://github.com/sympy/sympy.git 3bc91a30609223ca4e7da1a6feaf62bc179a6f7e
git -C /tmp/sympy-target checkout --detach FETCH_HEAD
python3.12 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/check_spec.py /tmp/sympy-target
.venv/bin/python scripts/check_boundaries.py /tmp/sympy-target
# Frozen upstream test: known failure from missing asin import, after selected assertions.
(cd /tmp/sympy-target && "$OLDPWD/.venv/bin/python" -m pytest sympy/assumptions/tests/test_refine.py -k conjugate -q)
# Optional test-only repair in a temporary file; target checkout remains unchanged.
cp /tmp/sympy-target/sympy/assumptions/tests/test_refine.py /tmp/test_refine_repaired.py
patch /tmp/test_refine_repaired.py < spec/patches/test-imports.patch
PYTHONPATH=/tmp/sympy-target .venv/bin/python -m pytest /tmp/test_refine_repaired.py -k conjugate -q
```

The unmodified upstream test has a missing-import failure; the separately
patched test passes. Our selected integration and boundary checks pass on the
unmodified target. See [validation details and outputs](spec/target.md#validation).
CI checks the frozen source and selected integration cases. The drift checker
is **not a proof of Python/Lean correspondence**.

Known exclusions: exceptional values (`oo`, `zoo`, `nan`), logarithm at zero,
negative-real logarithms, powers and square roots, inverse trigonometric
functions, general expression evaluation, and correctness of `ask`. Finite
variables alone do not ensure a compound expression is finite. Earlier
handler branches and expression construction can prevent a generic branch
from being reached. The existing [real-power example](LeanIdea/Basic.lean)
is outside the certified milestone.

Read the [frozen target and trusted contracts](spec/target.md),
[machine-readable mapping](spec/rules.json), [attributed source snapshot](spec/source/NOTICE.md),
and [implementation plan](PROOF_PLAN.md). Original work is [MIT licensed](LICENSE);
copied SymPy source retains its [BSD license](spec/source/LICENSE).

Permanent proof snapshot: [`e8f4500`](https://github.com/tilorc-bot/sympy-conjugate-lean/tree/e8f450009d7d5d2d56ec906f2cc0a4e541640053). The theorem links above are pinned to this first proof commit.

The first proof commit is tagged [`pilot-v0.1`](https://github.com/tilorc-bot/sympy-conjugate-lean/tree/pilot-v0.1) after its [successful GitHub CI run](https://github.com/tilorc-bot/sympy-conjugate-lean/actions/runs/34650602854). An independent fresh local checkout also [built successfully](spec/results/fresh-build.txt).

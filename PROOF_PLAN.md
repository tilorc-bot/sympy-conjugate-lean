# Plan: certify the simplest conjugation rules in SymPy PR #29173

## Goal and scope

Start with the two easiest rules: conjugation fixes a real value, and
conjugation negates a purely imaginary value. Then certify the logarithm rule
away from its branch cut as the first small analytic milestone. Publish the
proofs in a dedicated public GitHub repository with a readable explanation,
direct source links, and a reproducible CI build.

The intended claim is narrow: these selected rewrite branches preserve their
mathematical meaning under explicit domain and assumptions contracts. This is
not a proof of the entire PR or of SymPy's assumptions engine.

The supplied research report is a starting point, not the frozen specification.
Check the actual code at a recorded commit before deriving obligations.

## 1. Freeze the Python target

Inspect [SymPy PR #29173](https://github.com/sympy/sympy/pull/29173) and record
its exact head commit. Read `refine_conjugate`, its dispatch registration, and
the relevant tests at that commit.

Create `spec/target.md` containing:

- The full SymPy commit SHA and permanent links to the relevant source lines.
- The exact selected Python branches, including their order and earlier
  conditions that can prevent them from being reached.
- The input pattern, guard, and output expression for each selected rule.
- The SymPy version and commands used to run the relevant tests.

Use these expected rules only after checking them against that source:

| Rule ID | Original | Guard | Replacement |
| --- | --- | --- | --- |
| `conjugate.real` | `conjugate(x)` | `Q.real(x)` | `x` |
| `conjugate.imaginary` | `conjugate(x)` | `Q.imaginary(x)` | `-x` |
| `conjugate.log.off_cut` | `conjugate(log(x))` | `Q.complex(x) & ~Q.nonpositive(x)` | `log(conjugate(x))` |

For the generic rules, `x` denotes the entire argument of `conjugate`, which
can itself be a compound expression. Finite variables alone do not establish
that every compound expression has a finite value.

**Done when:** a reviewer can identify exactly which code and branches the
proof is intended to cover without consulting a moving PR head.

## 2. Prove the elementary core

Create `LeanIdea/Conjugate/Basic.lean` with small, named theorems over `ℂ`:

```text
z.im = 0  →  conj z = z
z.re = 0  →  conj z = -z
```

Use existing complex conjugation lemmas or prove equality by real and imaginary
parts. Do not introduce custom axioms or use `sorry`.

Define the mathematical predicate interpretations in
`LeanIdea/Conjugate/Guards.lean`. The real predicate implies zero imaginary
part. SymPy's imaginary predicate must imply zero real part; inspect whether
its definition also excludes zero. The theorem may safely use the weaker
condition `z.re = 0`, but document the direction of the implication.

State explicitly that positive `Q.real` and `Q.imaginary` answers supply a
finite-complex interpretation under the assumptions contract. Bare negations
of these predicates do not supply that contract.

**Done when:** both identities and their mathematical guard bridges compile,
and their statements make the domain assumptions visible.

## 3. Add the off-cut logarithm rule

The existing `LeanIdea/Basic.lean` already contains a compiled wrapper around
`Complex.log_conj`. Reuse or move it rather than duplicating the proof.

Define:

```lean
def OnNonpositiveRealRay (z : ℂ) : Prop :=
  z.im = 0 ∧ z.re ≤ 0
```

Prove the bridge from `¬ OnNonpositiveRealRay z` to `z.arg ≠ Real.pi` using
mathlib's argument lemmas. Also prove that the guard excludes zero and is
preserved by conjugation. These facts justify interpreting both logarithms
as ordinary principal logarithms.

Expose a final theorem with the guard-shaped hypothesis:

```text
¬ OnNonpositiveRealRay z → conj (Complex.log z) = Complex.log (conj z)
```

Explain the semantic boundary: mathlib's value at `log 0` does not model
SymPy's exceptional value. This rule must exclude zero even if a totalized
Lean identity happens to hold there.

The existing real-power example can remain as an example, but it is outside
the certified milestone until its Python guard and zero-base cases receive
the same review.

**Done when:** the public theorem uses the translated Python guard rather
than leaving the reviewer to supply an `arg ≠ π` assumption.

## 4. Connect guards and rewrites to a precise contract

Use a small rule model in `LeanIdea/Conjugate/Soundness.lean`. It only needs
the three selected rule identifiers, their guard predicates, and their left
and right denotations at a finite value. A general SymPy expression AST is
unnecessary for this milestone.

Prove a theorem of the following shape:

```text
for every selected rule and finite input value,
if its interpreted guard holds, its left and right denotations are equal
```

For the link to Python, write down these trusted contracts separately:

1. A successful `ask(P, A)` answer entails the mathematical interpretation
   of `P` for valuations satisfying `A`.
2. A positive finite-domain predicate on the relevant expression supplies
   its interpretation as a value of `ℂ`.
3. On the admitted domain, SymPy conjugation and principal logarithm agree
   with the Lean operations used in the theorem.
4. The recorded Python branch has the pattern, guard, and replacement
   represented by the selected rule.

Express logical contracts as explicit hypotheses where applicable, not new
global Lean axioms. Document which correspondence claims remain manually
reviewed. In particular, a source hash does not prove Python semantics or
the correctness of `ask`.

**Done when:** the README can distinguish kernel-checked identities and
guard implications from the assumptions needed to apply them to Python.

## 5. Record source correspondence and validate boundaries

Create `spec/rules.json` mapping each stable rule ID to its Python pattern,
guard, replacement, Lean theorem name, and frozen source commit. Record a
SHA-256 digest of the relevant handler source with an explicit extraction
method.

Add `scripts/check_spec.py` to compare a supplied SymPy checkout with the
recorded target and source digest. Make a mismatch fail with instructions to
review the changed branches and update the proof mapping. Label this a drift
check, not a proof of code correspondence. Include the selected source
snapshot with attribution so ordinary review does not need a second checkout.

Run the selected SymPy tests at the frozen commit. If they fail because of
unrelated PR cleanup, record the failure and keep any local repair as a
separate explicit patch; do not silently change the claimed target.

Check representative guard boundaries: real values, nonzero imaginary
values, zero, negative reals, finite non-real values, and exceptional values
such as `oo`, `zoo`, and `nan`. For the log rule, distinguish whether its
guard fires from any simplification performed elsewhere in SymPy. These
checks validate the integration assumptions; they do not replace proofs.

**Done when:** the source mapping is reviewable, drift is detected, and test
results and any unresolved limitations are recorded.

## 6. Create a GitHub repository for easy proof review

Proposed repository name: `sympy-conjugate-lean`.

First prepare the local files and README, then initialize Git and commit the
reviewable result. Determine the intended GitHub owner from the authenticated
`gh` account and confirm that the proposed name is available. During execution
of this plan, establish authorization for public publication before creating
and pushing the repository. Writing this plan does not itself create a repo.

Use `gh repo create` to create the public repository under that owner, add
the remote, and push the prepared commit. Avoid changing or pushing to SymPy's
repository. Choose and document a license, preserving attribution and any
license requirements for copied SymPy source.

The repository landing page should provide, in this order:

1. A one-paragraph statement of exactly what is proved and what is trusted.
2. A small table linking each selected Python branch to its Lean theorem.
3. The two elementary identities and the guarded log identity in readable
   mathematical notation.
4. A build-status badge linked to the proof-checking workflow.
5. Copy-and-paste reproduction commands and the pinned versions.
6. Known exclusions and links to the specification and this plan.

Use GitHub's rendered README and direct `.lean` source links as the initial
proof viewer. No separate website is needed. Include permanent links for the
first completed proof commit, and tag it `pilot-v0.1` after CI passes.

Suggested layout:

```text
README.md
PROOF_PLAN.md
lean-toolchain
lakefile.toml
lake-manifest.json
LeanIdea.lean
LeanIdea/Conjugate/Basic.lean
LeanIdea/Conjugate/Guards.lean
LeanIdea/Conjugate/Log.lean
LeanIdea/Conjugate/Soundness.lean
spec/target.md
spec/rules.json
spec/source/
scripts/check_spec.py
.github/workflows/lean.yml
```

**Done when:** a visitor can navigate from the mathematical claim to the
actual proof and its passing build in a few clicks.

## 7. Make the proof reproducible in CI

Add a GitHub Actions workflow for pushes and pull requests that installs elan,
uses the committed toolchain and manifest, fetches the needed mathlib cache,
and runs `lake build`. Pin third-party actions to reviewed commit SHAs.
Do not run an unpinned dependency update in CI.

Ensure every certified module is imported by the default build target. Reject
unfinished proofs, treat warnings as errors for the project's proof modules,
and inspect `#print axioms` for the final theorems. Record that only expected
Lean/mathlib foundational axioms appear, with no `sorryAx` or project-specific
assumed correctness axioms. Check the source manifest against the frozen
Python target in CI as well.

Document fresh-checkout reproduction:

```bash
git clone https://github.com/OWNER/sympy-conjugate-lean.git
cd sympy-conjugate-lean
lake exe cache get Mathlib.Analysis.SpecialFunctions.Pow.Complex
lake build
```

Replace `OWNER` before publishing. Adjust the cache imports if the finished
proofs use additional modules. Include separate commands for the Python source
drift check and selected SymPy tests, with their dependencies pinned.

**Done when:** a fresh checkout passes locally and on GitHub, and the public
README accurately describes the verified scope.

## Completion checklist

- [ ] SymPy target commit and three selected branches recorded.
- [ ] Real and imaginary conjugation proofs completed.
- [ ] Off-cut log guard bridge and final theorem completed.
- [ ] Selected-rule soundness theorem completed.
- [ ] Trusted assumptions and semantic exclusions documented.
- [ ] Source manifest, drift check, and boundary checks completed.
- [ ] Public GitHub repository created and populated with authorization.
- [ ] README links mathematical claims to source and passing CI.
- [ ] Fresh-checkout build succeeds; first milestone tagged.

After this milestone, consider negative-real logarithms, integer powers,
real powers, and square roots in that order of incremental scope. Keep inverse
trigonometric functions and extended-value semantics for a separate plan.

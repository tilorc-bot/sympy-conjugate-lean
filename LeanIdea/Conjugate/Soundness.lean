import LeanIdea.Conjugate.Log

namespace LeanIdea.Conjugate

inductive Rule where
  | real | imaginary | logOffCut
  deriving DecidableEq, Repr

def Rule.guard : Rule → ℂ → Prop
  | .real => IsReal
  | .imaginary => IsImaginary
  | .logOffCut => fun z => ¬ OnNonpositiveRealRay z

noncomputable def Rule.lhs : Rule → ℂ → ℂ
  | .real | .imaginary => fun z => (starRingEnd ℂ) z
  | .logOffCut => fun z => (starRingEnd ℂ) (Complex.log z)

noncomputable def Rule.rhs : Rule → ℂ → ℂ
  | .real => id
  | .imaginary => Neg.neg
  | .logOffCut => fun z => Complex.log ((starRingEnd ℂ) z)

/-- `z : ℂ` is the explicit finite-domain contract, for the whole relevant expression. -/
theorem selected_rule_sound (r : Rule) (z : ℂ) (h : r.guard z) : r.lhs z = r.rhs z := by
  cases r with
  | real => exact real_guard z h
  | imaginary => exact imaginary_guard z h
  | logOffCut => exact conjugate_log_off_cut z h

/-- Logical `ask` correctness is a hypothesis, never a global assumption.
The caller separately supplies a finite interpretation and operation correspondence. -/
theorem sound_of_successful_ask (accepted : Rule → ℂ → Prop)
    (ask_sound : ∀ r z, accepted r z → r.guard z)
    (r : Rule) (z : ℂ) (h : accepted r z) : r.lhs z = r.rhs z :=
  selected_rule_sound r z (ask_sound r z h)

end LeanIdea.Conjugate

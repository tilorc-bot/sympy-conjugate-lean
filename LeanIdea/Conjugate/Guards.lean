import LeanIdea.Conjugate.Basic

namespace LeanIdea.Conjugate

/-- Interpretations at an already supplied finite value; these do not implement `ask`. -/
def IsReal (z : ℂ) : Prop := z.im = 0
def IsImaginary (z : ℂ) : Prop := z.re = 0 ∧ z ≠ 0
def OnNonpositiveRealRay (z : ℂ) : Prop := z.im = 0 ∧ z.re ≤ 0

theorem real_guard (z : ℂ) (h : IsReal z) : (starRingEnd ℂ) z = z :=
  conjugate_real z h

theorem imaginary_guard (z : ℂ) (h : IsImaginary z) : (starRingEnd ℂ) z = -z :=
  conjugate_imaginary z h.1

end LeanIdea.Conjugate

import Mathlib.Analysis.SpecialFunctions.Complex.Log

namespace LeanIdea.Conjugate

/-- Conjugation fixes a finite complex value with zero imaginary part. -/
theorem conjugate_real (z : ℂ) (hz : z.im = 0) :
    (starRingEnd ℂ) z = z := by
  apply Complex.ext <;> simp [hz]

/-- The identity also holds at zero, although SymPy's imaginary predicate excludes it. -/
theorem conjugate_imaginary (z : ℂ) (hz : z.re = 0) :
    (starRingEnd ℂ) z = -z := by
  apply Complex.ext <;> simp [hz]

end LeanIdea.Conjugate

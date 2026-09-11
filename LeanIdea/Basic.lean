import Mathlib.Analysis.SpecialFunctions.Pow.Complex

/-! Small compiled examples for the SymPy conjugation verification pilot.
These prove finite-complex identities, not Python implementation correctness.
-/

namespace LeanIdea

theorem conjugate_cpow_real_off_cut
    (z : ℂ) (r : ℝ) (hz : z.arg ≠ Real.pi) :
    (starRingEnd ℂ) (z ^ (r : ℂ)) =
      ((starRingEnd ℂ) z) ^ (r : ℂ) := by
  simpa using (Complex.conj_cpow z (r : ℂ) hz).symm

end LeanIdea

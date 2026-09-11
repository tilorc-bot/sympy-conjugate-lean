import LeanIdea.Conjugate.Guards

namespace LeanIdea.Conjugate

theorem off_cut_arg (z : ℂ) (h : ¬ OnNonpositiveRealRay z) : z.arg ≠ Real.pi := by
  intro heq
  obtain ⟨hre, him⟩ := Complex.arg_eq_pi_iff.mp heq
  exact h ⟨him, le_of_lt hre⟩

theorem off_cut_ne_zero (z : ℂ) (h : ¬ OnNonpositiveRealRay z) : z ≠ 0 := by
  intro hz
  subst z
  exact h ⟨rfl, le_refl 0⟩

theorem off_cut_conj (z : ℂ) (h : ¬ OnNonpositiveRealRay z) :
    ¬ OnNonpositiveRealRay ((starRingEnd ℂ) z) := by
  simpa [OnNonpositiveRealRay] using h

/-- Both principal logarithms have nonzero inputs, unlike SymPy's exceptional `log(0)`. -/
theorem conjugate_log_off_cut (z : ℂ) (h : ¬ OnNonpositiveRealRay z) :
    (starRingEnd ℂ) (Complex.log z) = Complex.log ((starRingEnd ℂ) z) := by
  simpa using (Complex.log_conj z (off_cut_arg z h)).symm

end LeanIdea.Conjugate

import ArmReplay

set_option maxRecDepth 32768
set_option maxHeartbeats 15000000
set_option cbv.maxSteps 2000000

def oldSum := Replay.sum before_sum Replay.beforeLayout
def newSum := Replay.sum after_sum Replay.afterLayout
def oldBound := Replay.bound before_bound before_capture
def newBound := Replay.bound after_bound after_capture

theorem fixed_sum_matches (x : Dataset) : newSum x = some (mathematicalSum x) := by
  have all : rows.all (fun row => decide (newSum row = some (mathematicalSum row))) = true := by
    cbv
  exact of_decide_eq_true (List.all_eq_true.mp all x (row_mem x))

theorem fixed_bound_matches (d : Budget) : newBound d = some (mathematicalBound d) := by
  have all : (List.finRange 5).all
      (fun k => decide (newBound k = some (mathematicalBound k))) = true := by
    cbv
  exact of_decide_eq_true (List.all_eq_true.mp all d (List.mem_finRange d))

theorem fixed_satisfies_sensitivity : Sensitivity newSum newBound := by
  intro x y d distance
  exact ⟨mathematicalSum x, mathematicalSum y, mathematicalBound d,
    fixed_sum_matches x, fixed_sum_matches y, fixed_bound_matches d,
    mathematical_sensitivity x y d distance⟩

def witnessLeft : Dataset := (0, 0)
def witnessRight : Dataset := (0, 3)

theorem historical_witness :
    symmetricDistance witnessLeft witnessRight = 2 ∧
      oldSum witnessLeft = some 0 ∧ oldSum witnessRight = some 3 ∧
      oldBound 2 = some 2 := by
  exact ⟨by decide, by cbv, by cbv, by cbv⟩

theorem old_violates_sensitivity : ¬ Sensitivity oldSum oldBound := by
  intro sound
  obtain ⟨dist, left, right, bound⟩ := historical_witness
  have distance : symmetricDistance witnessLeft witnessRight ≤ (2 : Budget).val := by
    rw [dist]
    decide
  obtain ⟨a, b, limit, ha, hb, hlimit, hchange⟩ := sound witnessLeft witnessRight 2 distance
  rw [left] at ha
  rw [right] at hb
  rw [bound] at hlimit
  cases ha
  cases hb
  cases hlimit
  exact (by decide : ¬ absoluteDifference 0 3 ≤ 2) hchange

#print axioms historical_witness
#print axioms old_violates_sensitivity
#print axioms fixed_satisfies_sensitivity

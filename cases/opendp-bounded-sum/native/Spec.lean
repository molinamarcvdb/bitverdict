-- Public size and bounds for this pilot: exactly two i32 records in [0, 3].
abbrev Dataset := Fin 4 × Fin 4
abbrev Budget := Fin 5

def rows : List Dataset :=
  (List.finRange 4).flatMap fun a => (List.finRange 4).map fun b => (a, b)

theorem row_mem (x : Dataset) : x ∈ rows := by
  rcases x with ⟨a, b⟩
  exact List.mem_flatMap.mpr ⟨a, List.mem_finRange a, List.mem_map.mpr ⟨b, List.mem_finRange b, rfl⟩⟩

def count (x : Dataset) (value : Fin 4) : Nat :=
  (if x.1 = value then 1 else 0) + (if x.2 = value then 1 else 0)

-- Multiset symmetric difference. Each replacement costs a removal and an insertion.
def symmetricDistance (x y : Dataset) : Nat :=
  2 * (2 - ((List.finRange 4).map fun v => min (count x v) (count y v)).sum)

def absoluteDifference (x y : Nat) : Nat := (x - y) + (y - x)

-- The same contract takes both programs as parameters. A trap or error cannot pass.
def Sensitivity (sum : Dataset → Option Nat) (bound : Budget → Option Nat) : Prop :=
  ∀ (x y : Dataset) (d : Budget), symmetricDistance x y ≤ d.val →
    ∃ sx sy b : Nat,
      sum x = some sx ∧ sum y = some sy ∧ bound d = some b ∧
      absoluteDifference sx sy ≤ b

def mathematicalSum (x : Dataset) : Nat := x.1.val + x.2.val

def mathematicalBound (d : Budget) : Nat := (d.val / 2) * 3

theorem mathematical_sensitivity (x y : Dataset) (d : Budget)
    (h : symmetricDistance x y ≤ d.val) :
    absoluteDifference (mathematicalSum x) (mathematicalSum y) ≤ mathematicalBound d := by
  have all : rows.all (fun a => rows.all (fun b => (List.finRange 5).all (fun k =>
      decide (symmetricDistance a b ≤ k.val →
        absoluteDifference (mathematicalSum a) (mathematicalSum b) ≤ mathematicalBound k)))) = true := by
    decide
  have atX := List.all_eq_true.mp all x (row_mem x)
  have atXY := List.all_eq_true.mp atX y (row_mem y)
  have atXYD := List.all_eq_true.mp atXY d (List.mem_finRange d)
  exact of_decide_eq_true atXYD h

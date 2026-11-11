import Inputs

def datasetTokens : Dataset → List (Fin 4)
  | 0 => [0]
  | 1 => [1, 0]
  | 2 => [1, 0, 2]
  | 3 => [1, 0, 3]

def tokenCount (x token : Dataset) : Nat :=
  (datasetTokens x).filter (fun value => decide (value = token)) |>.length

def sharedCount (x y : Dataset) : Nat :=
  (List.finRange 4).map (fun token => min (tokenCount x token) (tokenCount y token)) |>.sum

def symmetricDistance (x y : Dataset) : Nat :=
  (datasetTokens x).length + (datasetTokens y).length - 2 * sharedCount x y

def absoluteDifference (x y : Int) : Nat := (x - y).natAbs

def expectedBound (d : Budget) : Nat := 1073741824 * d.val

def Sensitivity (sum : Dataset → Option Int) (bound : Budget → Option Nat) : Prop :=
  ∀ x y : Dataset, ∀ d : Budget, symmetricDistance x y ≤ d.val →
    ∃ sx sy : Int, ∃ b : Nat,
      sum x = some sx ∧ sum y = some sy ∧ bound d = some b ∧
      absoluteDifference sx sy ≤ b

def rows : List Dataset := List.finRange 4

theorem row_mem (x : Dataset) : x ∈ rows := List.mem_finRange x

def mathematicalSum (x : Dataset) : Int :=
  ((datasetTokens x).map (fun token => Int.ofNat ([1073741823, 1073741824, 1, 0][token.val]!))).sum

theorem mathematical_sensitivity (x y : Dataset) (d : Budget)
    (h : symmetricDistance x y ≤ d.val) :
    absoluteDifference (mathematicalSum x) (mathematicalSum y) ≤ expectedBound d := by
  have all : rows.all (fun a => rows.all (fun b => (List.finRange 2).all (fun k =>
      decide (symmetricDistance a b ≤ k.val →
        absoluteDifference (mathematicalSum a) (mathematicalSum b) ≤ expectedBound k)))) = true := by
    decide
  have atX := List.all_eq_true.mp all x (row_mem x)
  have atXY := List.all_eq_true.mp atX y (row_mem y)
  have atXYD := List.all_eq_true.mp atXY d (List.mem_finRange d)
  exact of_decide_eq_true atXYD h

example : Dataset → Dataset → Nat := symmetricDistance
example : Int → Int → Nat := absoluteDifference
example : (Dataset → Option Int) → (Budget → Option Nat) → Prop := Sensitivity

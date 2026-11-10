import Inputs

def countInDataset (v : Fin 4) (x : Dataset) : Nat :=
  (if x.1 = v then 1 else 0) + (if x.2 = v then 1 else 0)

def minNat (a b : Nat) : Nat :=
  if a ≤ b then a else b

def symmetricDistance (x y : Dataset) : Nat :=
  let c0 := minNat (countInDataset 0 x) (countInDataset 0 y)
  let c1 := minNat (countInDataset 1 x) (countInDataset 1 y)
  let c2 := minNat (countInDataset 2 x) (countInDataset 2 y)
  let c3 := minNat (countInDataset 3 x) (countInDataset 3 y)
  4 - 2 * (c0 + c1 + c2 + c3)

def absoluteDifference (a b : Nat) : Nat :=
  if a ≤ b then b - a else a - b

def Sensitivity (sum : Dataset → Option Nat) (bound : Budget → Option Nat) : Prop :=
  ∀ x y : Dataset, ∀ d : Budget,
    symmetricDistance x y ≤ d.val →
      ∃ sx sy bd : Nat,
        (sum x = some sx) ∧ (sum y = some sy) ∧ (bound d = some bd) ∧
          (absoluteDifference sx sy ≤ bd)

example : Dataset → Dataset → Nat := symmetricDistance
example : Nat → Nat → Nat := absoluteDifference
example : (Dataset → Option Nat) → (Budget → Option Nat) → Prop := Sensitivity

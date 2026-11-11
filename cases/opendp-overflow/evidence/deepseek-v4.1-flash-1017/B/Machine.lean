import ReplayCore
import ClosureBytes

open Replay

def machineLayout : Replay.VectorLayout :=
  ⟨binary_capacityOffset, binary_pointerOffset, binary_lengthOffset⟩
def machineSum := Replay.sum binary_sum machineLayout
def machineBound (d : Budget) : Option Nat := some (1073741824 * d.val)

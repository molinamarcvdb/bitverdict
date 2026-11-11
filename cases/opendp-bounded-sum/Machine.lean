import Arm64.Trusted.ISA.Semantics
import Inputs
import ClosureBytes

open Arm64

namespace Replay

abbrev Image := List (Nat × List (BitVec 8))

def entry : BitVec 64 := 0x1000
def returned : BitVec 64 := 0x4000
def environment : BitVec 64 := 0x5000
def argument : BitVec 64 := 0x6000
def elements : BitVec 64 := 0x6100
def result : BitVec 64 := 0x7000
def stackTop : BitVec 64 := 0x9000

def runToReturn (p : Program) (fuel : Nat) (s : State) : Option State :=
  match s.status with
  | .Running =>
    if s.pc == returned then some s
    else
      match fuel with
      | 0 => none
      | remaining + 1 => do
        let instruction ← p.fetchMem s.mem s.pc
        runToReturn p remaining (p.evalInst instruction s)
  | _ => none

-- Each run starts at the actual Rust Fn::call entry with the fixture's capture
-- and argument in separate mapped memory. X8 is the indirect result pointer.
def byteAt (image : Image) (a : BitVec 64) : Option (BitVec 8) :=
  image.findSome? fun (offset, bytes) =>
    bytes[(a - (entry + BitVec.ofNat 64 offset)).toNat]?

def initialMemory (image : Image) : Memory :=
  Memory.ofFn
    (fun a =>
      if result ≤ a && a < result + 64 then 0xff
      else (byteAt image a).getD 0)
    (fun a =>
      if environment ≤ a && a < stackTop then some Perm.rw
      else if (byteAt image a).isSome then some Perm.rx
      else none)

def execute (image : Image) (mem : Memory) : Option State :=
  let p : Program := { base := entry, code := [], svc := noSyscalls }
  let start : State := { pc := entry, mem := mem }
  let start := (start.writeReg64 .x0 environment)
    |>.writeReg64 .x1 argument
    |>.writeReg64 .x8 result
    |>.writeReg64 .sp stackTop
    |>.writeReg64 .x30 returned
  runToReturn p 96 start

structure VectorLayout where
  capacityOffset : Nat
  pointerOffset : Nat
  lengthOffset : Nat

def runSum (image : Image) (layout : VectorLayout) (x : Dataset) : Option State :=
  let mem := initialMemory image
  let mem := mem.write64 (argument + BitVec.ofNat 64 layout.capacityOffset) 2
    |>.write64 (argument + BitVec.ofNat 64 layout.pointerOffset) elements
    |>.write64 (argument + BitVec.ofNat 64 layout.lengthOffset) 2
    |>.write32 elements (BitVec.ofNat 32 x.1.val)
    |>.write32 (elements + 4) (BitVec.ofNat 32 x.2.val)
  execute image mem

def runBound (image : Image) (capture : Nat) (d : Budget) : Option State :=
  let mem := initialMemory image
  let mem := mem.write32 environment (BitVec.ofNat 32 capture)
    |>.write32 argument (BitVec.ofNat 32 d.val)
  execute image mem

-- Rust 1.94.1's compiled Ok(i32) writes the niche word and the i32 payload.
def readOk (finish : State) : Option Nat := do
  if finish.mem.read64 result != 0x8000000000000001 then none
  else
    let word := finish.mem.read32 (result + 8)
    if word.toInt < 0 then none else some word.toNat

def sum (image : Image) (layout : VectorLayout) (x : Dataset) : Option Nat :=
  (runSum image layout x).bind readOk

def bound (image : Image) (capture : Nat) (d : Budget) : Option Nat :=
  (runBound image capture d).bind readOk

end Replay

def machineLayout : Replay.VectorLayout :=
  ⟨binary_capacityOffset, binary_pointerOffset, binary_lengthOffset⟩
def machineSum := Replay.sum binary_sum machineLayout
def machineBound := Replay.bound binary_bound binary_capture

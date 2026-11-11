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

def datasetInputs : Dataset → List Nat
  | 0 => [1073741823]
  | 1 => [1073741824, 1073741823]
  | 2 => [1073741824, 1073741823, 1]
  | 3 => [1073741824, 1073741823, 0]

def writeElements (memory : Memory) (values : List Nat) : Memory :=
  (values.zipIdx).foldl
    (fun memory (value, index) =>
      memory.write32 (elements + BitVec.ofNat 64 (index * 4)) (BitVec.ofNat 32 value))
    memory

def runSum (image : Image) (layout : VectorLayout) (x : Dataset) : Option State :=
  let values := datasetInputs x
  let mem := initialMemory image
  let mem := mem.write64 (argument + BitVec.ofNat 64 layout.capacityOffset) 8
    |>.write64 (argument + BitVec.ofNat 64 layout.pointerOffset) elements
    |>.write64 (argument + BitVec.ofNat 64 layout.lengthOffset) values.length
  let mem := writeElements mem values
  execute image mem

-- Rust 1.94.1 writes the successful Result<i32, Error> through the return slot.
def readOk (finish : State) : Option Int := do
  if finish.mem.read64 result != 0x8000000000000001 then none
  else
    let word := finish.mem.read32 (result + 8)
    some word.toInt

def sum (image : Image) (layout : VectorLayout) (x : Dataset) : Option Int :=
  (runSum image layout x).bind readOk

end Replay

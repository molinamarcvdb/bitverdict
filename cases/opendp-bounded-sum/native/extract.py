"""Extract the actual closure bodies from the linked ARM64 Mach-O probes."""

from pathlib import Path
import re
import struct
import subprocess
import sys


def run(*args):
    return subprocess.check_output(args, text=True)


def text_section(binary):
    data = binary.read_bytes()
    magic, cpu, _, _, ncmds, *_ = struct.unpack_from("<8I", data)
    if (magic, cpu) != (0xFEEDFACF, 0x0100000C):
        raise ValueError(f"{binary} is not a little-endian ARM64 Mach-O")
    start = 32
    for _ in range(ncmds):
        cmd, size = struct.unpack_from("<2I", data, start)
        if cmd == 0x19:  # LC_SEGMENT_64
            nsects, = struct.unpack_from("<I", data, start + 64)
            for index in range(nsects):
                section = start + 72 + 80 * index
                name, segment, address, length, offset = struct.unpack_from(
                    "<16s16sQQI", data, section
                )
                if name.rstrip(b"\0") == b"__text" and segment.rstrip(b"\0") == b"__TEXT":
                    return address, data[offset:offset + length]
        start += size
    raise ValueError(f"{binary} has no __TEXT,__text section")


def extract(side, binary, log, disassembly):
    fixtures = {}
    for line in log.read_text().splitlines():
        if line.startswith("fixture "):
            _, name, *values = line.split()
            fixtures[name] = values

    start, section = text_section(binary)
    symbols = []
    for line in run("xcrun", "llvm-nm", "-n", "--defined-only", "--demangle", str(binary)).splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]+) [Tt] (.+)", line)
        if match and start <= int(match[1], 16) < start + len(section):
            symbols.append((int(match[1], 16), match[2]))
    anchor, = (address for address, name in symbols if name in ("_probe_anchor", "probe_anchor"))
    excerpts = []

    for name in ("sum", "bound"):
        delta, capture = fixtures[name]
        address = anchor + int(delta)
        target_names = [symbol for addr, symbol in symbols if addr == address]
        expected = ("Function",) if name == "sum" else ("StabilityRelation", "make_sized_bounded_sum")
        if not any("opendp" in symbol and any(part in symbol for part in expected) and "closure" in symbol
                   for symbol in target_names):
            raise ValueError(f"{side} {name} at {address:#x} is not the expected OpenDP closure: {target_names}")
        entries = [address]
        if name == "bound":
            helpers = ("InfCast$LT$u32", "ExactIntCast$LT$u32")
            if side == "after":
                helpers += ("InfMul$GT$::inf_mul",)
            for helper in helpers:
                entry, = {addr for addr, symbol in symbols
                          if "$LT$i32" in symbol and helper in symbol}
                entries.append(entry)
        segments = []
        for entry in entries:
            end = next(addr for addr, _ in symbols if addr > entry)
            code = section[entry - start:end - start]
            if not code or len(code) % 4 or not 0 <= entry - address <= 0x3000 - len(code):
                raise ValueError(f"invalid segment for {side} {name}: {entry:#x}")
            chunks = [code[i:i + 12] for i in range(0, len(code), 12)]
            lines = [", ".join(f"0x{byte:02x}" for byte in chunk) for chunk in chunks]
            segments.append(f"({entry - address}, [\n    " + ",\n    ".join(lines) + "\n  ])")
            excerpts.append(run("xcrun", "llvm-objdump", "-d", "--demangle",
                                f"--start-address={entry:#x}", f"--stop-address={end:#x}", str(binary)))
        print(f"def {side}_{name} : List (Nat × List (BitVec 8)) := [\n  "
              + ",\n  ".join(segments) + "\n]")
        if name == "bound":
            print(f"def {side}_capture : Nat := {int(capture)}")
        elif capture != "empty":
            raise ValueError(f"unexpected sum capture: {capture}")

    slots = [int(v) for v in fixtures["vec"]]
    if sorted(slots) != [0, 1, 2]:
        raise ValueError(f"invalid Vec slots: {slots}")
    for name, slot in zip(("capacity", "pointer", "length"), slots):
        print(f"def {side}_{name}Offset : Nat := {slot * 8}")
    disassembly.write_text("\n".join(excerpts))


print("-- Generated from the linked historical Rust builds by extract.py.")
for side in ("before", "after"):
    build = Path("build") / side
    extract(side, Path(sys.argv[1 if side == "before" else 2]),
            build / "native.log", build / "closures.asm")

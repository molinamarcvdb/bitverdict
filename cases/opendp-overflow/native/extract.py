"""Extract the bounded-sum closure from the two linked ARM64 binaries."""

from pathlib import Path
import re
import struct
import subprocess
import sys


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def text_section(binary: Path) -> tuple[int, bytes]:
    data = binary.read_bytes()
    magic, cpu, _, _, commands, *_ = struct.unpack_from("<8I", data)
    if (magic, cpu) != (0xFEEDFACF, 0x0100000C):
        raise ValueError(f"{binary} is not a little-endian ARM64 Mach-O")
    cursor = 32
    for _ in range(commands):
        command, size = struct.unpack_from("<2I", data, cursor)
        if command == 0x19:
            sections, = struct.unpack_from("<I", data, cursor + 64)
            for index in range(sections):
                section = cursor + 72 + 80 * index
                name, segment, address, length, offset = struct.unpack_from(
                    "<16s16sQQI", data, section
                )
                if name.rstrip(b"\0") == b"__text" and segment.rstrip(b"\0") == b"__TEXT":
                    return address, data[offset:offset + length]
        cursor += size
    raise ValueError(f"{binary} has no __TEXT,__text section")


def extract(side: str, binary: Path) -> str:
    start, section = text_section(binary)
    symbols = []
    for line in run("xcrun", "llvm-nm", "-n", "--defined-only", "--demangle", str(binary)).splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]+) [Tt] (.+)", line)
        if match and start <= int(match[1], 16) < start + len(section):
            symbols.append((int(match[1], 16), match[2]))

    log = binary.parent / "native.log"
    delta = None
    vector_slots = None
    for line in log.read_text(encoding="utf-8").splitlines():
        if line.startswith("fixture sum "):
            delta = int(line.split()[2])
        elif line.startswith("fixture vec "):
            vector_slots = [int(value) for value in line.split()[2:]]
    if delta is None:
        raise ValueError(f"{log} is missing the native sum closure address")
    if vector_slots is None or sorted(vector_slots) != [0, 1, 2]:
        raise ValueError(f"{log} is missing the expected Vec<i32> layout")

    anchor, = (address for address, name in symbols if name in ("_probe_anchor", "probe_anchor"))
    address = anchor + delta
    names = [name for current, name in symbols if current == address]
    if not any("opendp" in name and "Function" in name and "closure" in name for name in names):
        raise ValueError(f"{side} sum address is not an OpenDP function closure: {names}")
    end = next((current for current, _ in symbols if current > address), None)
    if end is None:
        raise ValueError(f"{side} sum closure has no following symbol")
    code = section[address - start:end - start]
    if not code or len(code) % 4 or len(code) > 0x3000:
        raise ValueError(f"invalid {side} sum closure size: {len(code)}")
    lines = [", ".join(f"0x{byte:02x}" for byte in code[offset:offset + 12])
             for offset in range(0, len(code), 12)]
    closure = (
        f"def {side}_sum : List (Nat × List (BitVec 8)) := [\n"
        "  (0, [\n    " + ",\n    ".join(lines) + "\n  ])\n]"
    )

    assembly = run("xcrun", "llvm-objdump", "-d", "--demangle",
                   f"--start-address={address:#x}", f"--stop-address={end:#x}", str(binary))
    fixtures = Path(__file__).resolve().parent.parent / "fixtures"
    (fixtures / f"{side}.asm").write_text(
        assembly.replace(str(binary), "compiled image"), encoding="utf-8"
    )
    offsets = [f"def {side}_{name}Offset : Nat := {slot * 8}"
               for name, slot in zip(("capacity", "pointer", "length"), vector_slots)]
    return closure + "\n" + "\n".join(offsets)


if len(sys.argv) != 3:
    raise SystemExit("Usage: extract.py BEFORE_BINARY AFTER_BINARY")

print("-- Extracted from the linked OpenDP Rust binaries.")
for name, path in zip(("before", "after"), sys.argv[1:]):
    print(extract(name, Path(path)))

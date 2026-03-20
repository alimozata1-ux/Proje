#!/usr/bin/env python3
"""
KONE VM (Python)

Mars32/Mars64 bytecode formatı için referans yorumlayıcı.
Bu araç C tabanlı `konevm` ile aynı opcode setini uygular
ve debug/inspect amaçlı daha ayrıntılı çıktı sağlar.
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import struct
import sys
from typing import List

OP_PUSH = 1
OP_ADD = 2
OP_PRINT = 3
OP_HALT = 255


@dataclasses.dataclass
class CPU:
    ip: int = 0
    halted: bool = False


@dataclasses.dataclass
class RAM:
    size: int

    def __post_init__(self) -> None:
        self.bytes = bytearray(self.size)


@dataclasses.dataclass
class Disk:
    size: int

    def __post_init__(self) -> None:
        self.bytes = bytearray(self.size)


@dataclasses.dataclass
class Framebuffer:
    width: int
    height: int

    def __post_init__(self) -> None:
        self.pixels = [0] * (self.width * self.height)


class VMRuntimeError(RuntimeError):
    pass


@dataclasses.dataclass
class KonePythonVM:
    debug: bool = False
    trace_stack: bool = False
    max_steps: int = 100_000

    def __post_init__(self) -> None:
        self.cpu = CPU()
        self.ram = RAM(1024 * 1024)
        self.disk = Disk(128 * 1024)
        self.fb = Framebuffer(320, 200)
        self.stack: List[int] = []
        self.program = b""
        self.arch = "M3"

    def load(self, path: pathlib.Path) -> None:
        data = path.read_bytes()
        if len(data) < 2:
            raise VMRuntimeError("program too small")
        if data[:2] not in (b"M3", b"M6"):
            raise VMRuntimeError("invalid Mars executable header")

        self.arch = data[:2].decode("ascii")
        self.program = data
        self.cpu.ip = 2
        self.cpu.halted = False
        self.stack.clear()

        if self.debug:
            print(f"[KONE VM PY] loaded={path} arch={self.arch} size={len(data)}")

    def _fetch_u32(self) -> int:
        if self.cpu.ip + 4 > len(self.program):
            raise VMRuntimeError("unexpected EOF while reading imm32")
        raw = self.program[self.cpu.ip : self.cpu.ip + 4]
        self.cpu.ip += 4
        return struct.unpack("<I", raw)[0]

    def _log(self, message: str) -> None:
        if self.debug:
            print(f"[KONE VM PY][debug] {message}")

    def _log_stack(self) -> None:
        if self.trace_stack:
            print(f"[KONE VM PY][stack] {self.stack}")

    def step(self) -> None:
        if self.cpu.halted:
            return
        if self.cpu.ip >= len(self.program):
            raise VMRuntimeError("instruction pointer out of bounds")

        op = self.program[self.cpu.ip]
        self.cpu.ip += 1

        if op == OP_PUSH:
            imm = self._fetch_u32()
            self.stack.append(int(imm))
            self._log(f"OP_PUSH {imm}")
            self._log_stack()
            return

        if op == OP_ADD:
            if len(self.stack) < 2:
                raise VMRuntimeError("stack underflow on OP_ADD")
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
            self._log(f"OP_ADD {a}+{b}={a+b}")
            self._log_stack()
            return

        if op == OP_PRINT:
            if not self.stack:
                raise VMRuntimeError("stack underflow on OP_PRINT")
            val = self.stack.pop()
            print(f"[KONE VM PY] {val}")
            self._log("OP_PRINT")
            self._log_stack()
            return

        if op == OP_HALT:
            self.cpu.halted = True
            self._log("OP_HALT")
            return

        raise VMRuntimeError(f"unknown opcode: {op}")

    def run(self) -> int:
        steps = 0
        while not self.cpu.halted:
            self.step()
            steps += 1
            if steps > self.max_steps:
                raise VMRuntimeError("step limit exceeded")
        self._log(f"completed in {steps} steps")
        return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KONE Python VM")
    p.add_argument("program", type=pathlib.Path, help=".mars32/.mars64 executable")
    p.add_argument("--debug", action="store_true", help="enable debug logs")
    p.add_argument("--trace-stack", action="store_true", help="print stack after each op")
    p.add_argument("--max-steps", type=int, default=100_000, help="max instruction count")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    vm = KonePythonVM(debug=args.debug, trace_stack=args.trace_stack, max_steps=args.max_steps)
    try:
        vm.load(args.program)
        return vm.run()
    except FileNotFoundError:
        print(f"error: file not found: {args.program}", file=sys.stderr)
        return 1
    except VMRuntimeError as exc:
        print(f"runtime error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

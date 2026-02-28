from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Node:
    line: int


@dataclass
class Block(Node):
    statements: List[Node] = field(default_factory=list)


@dataclass
class Assignment(Node):
    name: str
    expr: str


@dataclass
class Print(Node):
    expr: str


@dataclass
class Return(Node):
    expr: Optional[str] = None


@dataclass
class FunctionDef(Node):
    name: str
    body: Block
    is_async: bool = False


@dataclass
class FunctionCall(Node):
    name: str


@dataclass
class Command(Node):
    name: str
    args: str = ""


@dataclass
class If(Node):
    condition: str
    then_block: Block
    elif_blocks: List[tuple[str, Block]] = field(default_factory=list)
    else_block: Optional[Block] = None


@dataclass
class While(Node):
    condition: str
    body: Block


@dataclass
class For(Node):
    target: str
    iterator: str
    body: Block


@dataclass
class Import(Node):
    module: str
    alias: Optional[str] = None


@dataclass
class Expr(Node):
    expr: str


@dataclass
class Break(Node):
    pass


@dataclass
class Continue(Node):
    pass

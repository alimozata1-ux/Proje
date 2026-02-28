from __future__ import annotations

import asyncio
import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import ast_nodes as ast
from .builtins import register_builtin_commands
from .lexer import ProtonLexer
from .parser import ProtonParser
from .plugins import load_plugins
from .registry import CommandRegistry
from .sandbox import SandboxPolicy


class ProtonRuntimeError(Exception):
    pass


@dataclass
class ProtonContext:
    globals: dict[str, Any] = field(default_factory=dict)
    locals: dict[str, Any] = field(default_factory=dict)
    sandbox: SandboxPolicy = field(default_factory=SandboxPolicy)
    db: Any = None

    def eval_expr(self, expr: str) -> Any:
        scope = {**self.globals, **self.locals, "__builtins__": __builtins__}
        return eval(expr, scope, self.locals)


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class ProtonInterpreter:
    def __init__(self, plugin_dir: str | None = None):
        self.registry = CommandRegistry()
        register_builtin_commands(self.registry)
        self.context = ProtonContext()
        if plugin_dir:
            load_plugins(Path(plugin_dir), self.registry)

    def run(self, source: str) -> Any:
        tree = ProtonParser(ProtonLexer().tokenize(source)).parse()
        return self.execute_block(tree)

    def execute_block(self, block: ast.Block):
        result = None
        for stmt in block.statements:
            result = self.execute(stmt)
            self.context.locals["_"] = result
        return result

    def execute(self, node):
        try:
            match node:
                case ast.Assignment(name=name, expr=expr):
                    self.context.locals[name] = self.context.eval_expr(expr)
                case ast.Print(expr=expr):
                    print(self.context.eval_expr(expr) if expr else "")
                case ast.Return(expr=expr):
                    raise ReturnSignal(self.context.eval_expr(expr) if expr else None)
                case ast.FunctionDef(name=name, body=body, is_async=is_async):
                    if is_async:
                        async def fn():
                            try:
                                return self.execute_block(body)
                            except ReturnSignal as rs:
                                return rs.value
                    else:
                        def fn():
                            try:
                                return self.execute_block(body)
                            except ReturnSignal as rs:
                                return rs.value
                    self.context.locals[name] = fn
                case ast.FunctionCall(name=name):
                    fn = self.context.locals.get(name)
                    if not callable(fn):
                        raise ProtonRuntimeError(f"Undefined function {name}")
                    return fn()
                case ast.Command(name=name, args=args):
                    return self.registry.execute(name, args, self.context)
                case ast.If(condition=cond, then_block=tb, elif_blocks=eb, else_block=els):
                    if self.context.eval_expr(cond):
                        return self.execute_block(tb)
                    for cnd, blk in eb:
                        if self.context.eval_expr(cnd):
                            return self.execute_block(blk)
                    if els:
                        return self.execute_block(els)
                case ast.While(condition=cond, body=body):
                    while self.context.eval_expr(cond):
                        try:
                            self.execute_block(body)
                        except StopIteration:
                            break
                case ast.For(target=t, iterator=it, body=body):
                    for value in self.context.eval_expr(it):
                        self.context.locals[t] = value
                        try:
                            self.execute_block(body)
                        except StopIteration:
                            break
                case ast.Break():
                    raise StopIteration
                case ast.Continue():
                    return None
                case ast.Import(module=module, alias=alias):
                    mod = importlib.import_module(module)
                    self.context.locals[alias or module] = mod
                case ast.Expr(expr=expr):
                    return self.context.eval_expr(expr)
                case _:
                    raise ProtonRuntimeError(f"Unsupported node: {type(node).__name__}")
        except ReturnSignal:
            raise
        except Exception as exc:  # centralized error handling
            raise ProtonRuntimeError(f"Line {node.line}: {exc}") from exc
        return None


class ProtonREPL:
    def __init__(self, interpreter: ProtonInterpreter | None = None):
        self.interpreter = interpreter or ProtonInterpreter()

    def loop(self):
        print("Proton REPL. exit için 'quit'.")
        while True:
            line = input("proton> ").strip("\n")
            if line.strip() in {"quit", "exit"}:
                break
            try:
                result = self.interpreter.run(line)
                if result is not None:
                    print(result)
            except Exception as exc:
                print(f"Hata: {exc}")

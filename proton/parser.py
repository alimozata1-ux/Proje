from __future__ import annotations

from typing import List, Optional

from .ast_nodes import (
    Assignment,
    Block,
    Break,
    Command,
    Continue,
    Expr,
    For,
    FunctionCall,
    FunctionDef,
    If,
    Import,
    Print,
    Return,
    While,
)
from .lexer import TokenLine


class ProtonParserError(Exception):
    pass


class ProtonParser:
    def __init__(self, tokens: List[TokenLine]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Block:
        return self._parse_block(base_indent=0)

    def _peek(self) -> Optional[TokenLine]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _consume(self) -> TokenLine:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _parse_block(self, base_indent: int) -> Block:
        statements = []
        while (tok := self._peek()) is not None:
            if tok.indent < base_indent:
                break
            if tok.indent > base_indent:
                raise ProtonParserError(f"Unexpected indent at line {tok.line_no}")
            statements.append(self._parse_statement(base_indent))
        return Block(line=statements[0].line if statements else 1, statements=statements)

    def _parse_statement(self, indent: int):
        tok = self._consume()
        text = tok.content

        if text.startswith("#mod "):
            payload = text[5:].strip()
            if " as " in payload:
                module, alias = payload.split(" as ", 1)
                return Import(line=tok.line_no, module=module.strip(), alias=alias.strip())
            return Import(line=tok.line_no, module=payload)

        if text == "break>":
            return Break(line=tok.line_no)
        if text == "cont>":
            return Continue(line=tok.line_no)

        if text.startswith("@"):
            return Print(line=tok.line_no, expr=text[1:].strip())
        if text.startswith("=>"):
            return Return(line=tok.line_no, expr=text[2:].strip() or None)

        if text.endswith("->") and not text.startswith(("T", "bg", "every", "async")):
            name = text[:-2].strip()
            body = self._parse_expected_child_block(tok.line_no, indent)
            return FunctionDef(line=tok.line_no, name=name, body=body)

        if text == "async->":
            body = self._parse_expected_child_block(tok.line_no, indent)
            return FunctionDef(line=tok.line_no, name=f"__async_block_{tok.line_no}", body=body, is_async=True)

        if text.startswith("if:"):
            node = If(line=tok.line_no, condition=text[3:].strip(), then_block=self._parse_expected_child_block(tok.line_no, indent))
            while (next_tok := self._peek()) is not None and next_tok.indent == indent and next_tok.content.startswith("elif:"):
                self._consume()
                cond = next_tok.content[5:].strip()
                node.elif_blocks.append((cond, self._parse_expected_child_block(next_tok.line_no, indent)))
            next_tok = self._peek()
            if next_tok is not None and next_tok.indent == indent and next_tok.content.startswith("else:"):
                self._consume()
                node.else_block = self._parse_expected_child_block(next_tok.line_no, indent)
            return node

        if text.startswith("while:"):
            return While(line=tok.line_no, condition=text[6:].strip(), body=self._parse_expected_child_block(tok.line_no, indent))

        if text.startswith("for:"):
            payload = text[4:].strip()
            if " in " not in payload:
                raise ProtonParserError(f"Invalid for syntax at line {tok.line_no}")
            target, iterator = payload.split(" in ", 1)
            return For(line=tok.line_no, target=target.strip(), iterator=iterator.strip(), body=self._parse_expected_child_block(tok.line_no, indent))

        if ":" in text and not text.startswith(("sh:", "sys:")):
            left, right = text.split(":", 1)
            left = left.strip()
            right = right.strip()
            if left.isidentifier():
                return Assignment(line=tok.line_no, name=left, expr=right)

        first = text.split(maxsplit=1)[0]
        command_like = (
            first.endswith(">")
            or first in {"sh:", "sys:", "py:", "sandbox>", "T->", "bg>", "every>", "await>", "+:", "-:", "*:", "/:", "^:", "%:", "t:", "r<"}
            or (first.endswith(":") and not first[:-1].isidentifier())
        )
        if command_like:
            parts = text.split(maxsplit=1)
            name = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            return Command(line=tok.line_no, name=name, args=args)

        if text.isidentifier():
            return FunctionCall(line=tok.line_no, name=text)

        return Expr(line=tok.line_no, expr=text)

    def _parse_expected_child_block(self, line_no: int, parent_indent: int) -> Block:
        nxt = self._peek()
        if nxt is None or nxt.indent <= parent_indent:
            raise ProtonParserError(f"Expected indented block after line {line_no}")
        return self._parse_block(base_indent=nxt.indent)

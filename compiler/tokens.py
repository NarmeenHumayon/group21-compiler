# compiler/tokens.py
from dataclasses import dataclass
from typing import Any, Tuple

@dataclass
class Token:
    type: str
    value: Any = None
    pos: Tuple[int, int] = None  # (line, col)

    def __repr__(self):
        if self.value is None:
            return f"{self.type}()"
        return f"{self.type}({self.value!r})"


# keywords mapping used by lexers
KEYWORDS = {
    # english
    "fn": "Function",
    "function": "Function",
    "return": "Return",
    "if": "If",
    "else": "Else",
    "for": "For",
    "break": "Break",
    "true": "BoolLit",
    "false": "BoolLit",
    "int": "Int",
    "float": "Float",
    "bool": "Bool",
    "string": "String",
    # alternate tokens (samples)
    "ginti": "Int",
    "wapsi": "Return",
    "agar": "If",
    "warna": "Else",
    "duhrao": "For",
    "toro": "Break",
}

# single-char token mapping
SINGLE_CHARS = {
    '(': "ParenL", ')': "ParenR",
    '{': "BraceL", '}': "BraceR",
    '[': "BracketL", ']': "BracketR",
    ',': "Comma", ';': "Semicolon",
    '.': "Dot", ':': "Colon",
    '+': "AddOp", '-': "SubOp",
    '*': "MulOp", '/': "DivOp",
    '%': "ModOp", '!': "NotOp",
    '=': "AssignOp", '<': "LessThan", '>': "GreaterThan",
    '&': "Amp", '|': "Pipe",
}

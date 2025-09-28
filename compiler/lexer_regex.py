# compiler/lexer_regex.py
import re
from typing import List
from .tokens import Token, KEYWORDS, SINGLE_CHARS

class RegexLexer:
    def __init__(self, code: str):
        self.code = code
        # token spec: order matters (longer first)
        self.spec = [
            ("MULTI_COMMENT", r'/\*[\s\S]*?\*/'),
            ("LINE_COMMENT", r'//[^\n]*'),
            ("HASH_COMMENT", r'#[^\n]*'),
            ("String", r'"(?:\\.|[^"\\])*"'),
            ("FloatLit", r'\d+\.\d+|\d+\.(?=\D)|\.\d+'),
            ("IntLit", r'\d+'),
            ("EqualsOp", r'=='),
            ("NotEquals", r'!='),
            ("LessEq", r'<='),
            ("GreaterEq", r'>='),
            ("AndOp", r'&&'),
            ("OrOp", r'\|\|'),
            ("OP", r'[+\-*/%<>=!&|().{},;:\[\]]'),
            ("Identifier", r'(?!\d)\w+'),
            ("SKIP", r'[ \t]+'),
            ("NEWLINE", r'\n'),
            ("MISMATCH", r'.'),
        ]
        self.master = re.compile("|".join(f"(?P<{n}>{p})" for n,p in self.spec), re.UNICODE)

    def _unescape(self, raw: str) -> str:
        # simple unescape for common sequences; supports \n, \t, \r, \", \\, \x, \u.
        try:
            # use python's unicode_escape safely on bytes
            return bytes(raw, "utf-8").decode("unicode_escape")
        except Exception:
            return raw

    def tokenize(self) -> List[Token]:
        code = self.code
        line = 1
        col = 1
        tokens: List[Token] = []
        for mo in self.master.finditer(code):
            kind = mo.lastgroup
            text = mo.group()
            if kind == "NEWLINE":
                line += 1
                col = 1
                continue
            if kind in ("LINE_COMMENT", "MULTI_COMMENT", "HASH_COMMENT"):
                col += len(text)
                continue
            if kind == "SKIP":
                col += len(text)
                continue
            if kind == "MISMATCH":
                raise SyntaxError(f"Unexpected character {text!r} at {line}:{col}")
            if kind == "String":
                raw = text[1:-1]
                val = self._unescape(raw)
                tokens.append(Token("StringLit", val, (line, col)))
                col += len(text)
                continue
            if kind == "Identifier":
                key = text
                if key in KEYWORDS:
                    kt = KEYWORDS[key]
                    if kt == "BoolLit":
                        tokens.append(Token("BoolLit", True if key == "true" else False, (line,col)))
                    else:
                        tokens.append(Token(kt, None, (line,col)))
                else:
                    if text and text[0].isdigit():
                        raise SyntaxError(f"Identifier cannot start with digit: {text!r} at {line}:{col}")
                    tokens.append(Token("Identifier", text, (line,col)))
                col += len(text)
                continue
            if kind == "IntLit":
                tokens.append(Token("IntLit", int(text), (line,col)))
                col += len(text)
                continue
            if kind == "FloatLit":
                tokens.append(Token("FloatLit", float(text), (line,col)))
                col += len(text)
                continue
            if kind in ("EqualsOp","NotEquals","LessEq","GreaterEq","AndOp","OrOp"):
                tokens.append(Token(kind, None, (line,col)))
                col += len(text)
                continue
            if kind == "OP":
                ch = text
                # single char mapping
                if ch in SINGLE_CHARS:
                    tokens.append(Token(SINGLE_CHARS[ch], None, (line,col)))
                else:
                    tokens.append(Token(ch, None, (line,col)))
                col += len(text)
                continue
        tokens.append(Token("EOF", None, (line,col)))
        return tokens

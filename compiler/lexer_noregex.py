# compiler/lexer_noregex.py
from typing import List
from .tokens import Token, KEYWORDS, SINGLE_CHARS
import unicodedata

def is_ident_start(ch: str) -> bool:
    if ch == '_': return True
    cat = unicodedata.category(ch)
    return cat.startswith('L') or cat == 'Nl'

def is_ident_part(ch: str) -> bool:
    if ch == '_': return True
    cat = unicodedata.category(ch)
    return cat.startswith('L') or cat.startswith('M') or cat == 'Nd' or cat == 'Pc' or cat == 'Nl'

class NoRegexLexer:
    def __init__(self, code: str):
        self.src = code
        self.i = 0
        self.len = len(code)
        self.line = 1
        self.col = 1

    def _peek(self) -> str:
        return self.src[self.i] if self.i < self.len else ''

    def _next(self) -> str:
        ch = self._peek()
        self.i += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _peek_ahead(self) -> str:
        return self.src[self.i+1] if (self.i+1) < self.len else ''

    def _peek_two(self) -> str:
        if (self.i+1) < self.len:
            return self.src[self.i:self.i+2]
        return ''

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.i < self.len:
            ch = self._peek()
            # whitespace
            if ch.isspace():
                self._next()
                continue
            # comments
            if self._peek_two() == '//':
                while self._peek() and self._peek() != '\n':
                    self._next()
                continue
            if self._peek_two() == '/*':
                self._next(); self._next()
                while self._peek_two() != '*/':
                    if self._peek() == '':
                        raise SyntaxError("Unterminated comment")
                    self._next()
                self._next(); self._next()
                continue
            if ch == '#':
                while self._peek() and self._peek() != '\n':
                    self._next()
                continue
            # string
            if ch == '"':
                pos = (self.line, self.col)
                self._next()
                buf = []
                while True:
                    c = self._peek()
                    if c == '':
                        raise SyntaxError("Unterminated string literal")
                    if c == '"':
                        self._next()
                        break
                    if c == '\\':
                        self._next()
                        esc = self._peek()
                        if esc == 'n':
                            buf.append('\n'); self._next()
                        elif esc == 't':
                            buf.append('\t'); self._next()
                        elif esc == 'r':
                            buf.append('\r'); self._next()
                        elif esc == '"':
                            buf.append('"'); self._next()
                        elif esc == '\\':
                            buf.append('\\'); self._next()
                        else:
                            # raw next char
                            buf.append(self._next())
                    else:
                        buf.append(self._next())
                tokens.append(Token("StringLit", ''.join(buf), pos))
                continue
            # numbers
            if ch.isdigit() or (ch == '.' and self._peek_ahead().isdigit()):
                pos = (self.line, self.col)
                buf = []
                dot_count = 0
                while self._peek() and (self._peek().isdigit() or self._peek() == '.'):
                    if self._peek() == '.': dot_count += 1
                    buf.append(self._next())
                s = ''.join(buf)
                if dot_count == 0:
                    tokens.append(Token("IntLit", int(s), pos))
                else:
                    tokens.append(Token("FloatLit", float(s), pos))
                continue
            # identifier
            if is_ident_start(ch):
                pos = (self.line, self.col)
                buf = []
                while self._peek() and is_ident_part(self._peek()):
                    buf.append(self._next())
                w = ''.join(buf)
                if w in KEYWORDS:
                    kt = KEYWORDS[w]
                    if kt == "BoolLit":
                        tokens.append(Token("BoolLit", True if w == "true" else False, pos))
                    else:
                        tokens.append(Token(kt, None, pos))
                else:
                    if w and w[0].isdigit():
                        raise SyntaxError(f"Identifier cannot start with digit: {w!r} at {pos}")
                    tokens.append(Token("Identifier", w, pos))
                continue
            # two-char ops
            two = self._peek_two()
            if two in ("==","!=","<=",">=","&&","||"):
                map2 = {"==":"EqualsOp","!=":"NotEquals","<=":"LessEq",">=":"GreaterEq","&&":"AndOp","||":"OrOp"}
                tokens.append(Token(map2[two], None, (self.line,self.col)))
                self._next(); self._next()
                continue
            # single char punctuation
            if ch in SINGLE_CHARS:
                tname = SINGLE_CHARS[ch]
                tokens.append(Token(tname, None, (self.line,self.col)))
                self._next()
                continue
            # fallback single-char operators
            if ch in '+-*/%<>=!&|.,;[]:':
                map_single = {
                    '+': "AddOp", '-': "SubOp", '*': "MulOp", '/': "DivOp",
                    '%': "ModOp", '<': "LessThan", '>': "GreaterThan", '=': "AssignOp",
                    '!': "NotOp", '&': "Amp", '|': "Pipe", '.': "Dot", ',': "Comma",
                    ';': "Semicolon", '[': "BracketL", ']': "BracketR", ':': "Colon"
                }
                tokens.append(Token(map_single[ch], None, (self.line,self.col)))
                self._next()
                continue
            raise SyntaxError(f"Unknown character {ch!r} at {self.line}:{self.col}")
        tokens.append(Token("EOF", None, (self.line,self.col)))
        return tokens

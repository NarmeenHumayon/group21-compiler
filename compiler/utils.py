# utils.py  –  helper functions for the tiny compiler
import sys
import io
import re


# ---------- Character-type helpers ----------
def is_alpha(ch: str) -> bool:
    """Return True if character is a Unicode alphabetic letter or underscore."""
    return ch.isalpha() or ch == "_"


def is_digit(ch: str) -> bool:
    """Return True if character is a decimal digit."""
    return ch.isdigit()


def is_alnum(ch: str) -> bool:
    """Return True if character is alphanumeric or underscore."""
    return is_alpha(ch) or is_digit(ch)


def is_space(ch: str) -> bool:
    """Return True if character is whitespace (space, tab, newline)."""
    return ch in (" ", "\t", "\r", "\n")


# ---------- File helpers ----------
# compiler/utils.py
def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()



# ---------- Error reporting ----------
def report_error(src: str, line: int, col: int, msg: str) -> None:
    """
    Pretty-print an error message showing line/column and the
    offending line of code with a caret pointing at the column.
    """
    lines = src.splitlines()
    line_text = lines[line - 1] if 0 <= line - 1 < len(lines) else ""
    print(f"\n[SyntaxError] line {line}, col {col}: {msg}")
    print(f"    {line_text}")
    print("    " + " " * (col - 1) + "^")
    sys.exit(1)


# ---------- Escaped string utilities ----------
_escape_map = {
    "\\n": "\n",
    "\\t": "\t",
    "\\r": "\r",
    "\\\"": "\"",
    "\\'": "'",
    "\\\\": "\\",
}

def unescape_string(s: str) -> str:
    """
    Convert escape sequences (\\n, \\t, \\\", \\\\ …) inside a string literal
    into real characters.
    """
    for k, v in _escape_map.items():
        s = s.replace(k, v)
    return s


# ---------- Debug helper ----------
def debug_tokens(tokens):
    """Print all tokens in a single line for quick debugging."""
    print("[" + ", ".join(str(tok) for tok in tokens) + "]")

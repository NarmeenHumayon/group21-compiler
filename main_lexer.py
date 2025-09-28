# main_lexer.py
import sys
from compiler.utils import read_file
from compiler.lexer_regex import RegexLexer
from compiler.lexer_noregex import NoRegexLexer

def main():
    if len(sys.argv) != 2:
        print("Usage: python main_lexer.py <sourcefile>")
        sys.exit(1)
    fname = sys.argv[1]
    code = read_file(fname)

    print("=== Regex Lexer ===")
    rlex = RegexLexer(code)
    toks = rlex.tokenize()
    for t in toks:
        print(t)

    print("\n=== No-Regex Lexer ===")
    nlex = NoRegexLexer(code)
    toks2 = nlex.tokenize()
    for t in toks2:
        print(t)

if __name__ == "__main__":
    main()

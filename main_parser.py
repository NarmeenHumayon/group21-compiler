# main_parser.py
import sys
from compiler.lexer_regex import RegexLexer
from compiler.parser import Parser, pretty_print_ast

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_parser.py <sourcefile>")
        sys.exit(1)

    src_path = sys.argv[1]
    with open(src_path, "r", encoding="utf-8") as f:
        code = f.read()

    print(f"=== Parsing: {src_path} ===\n")

    # Step 1: Lexical analysis
    lexer = RegexLexer(code)
    tokens = lexer.tokenize()

    print("=== Tokens ===")
    for t in tokens:
        print(t)
    print("\n=== AST ===")

    # Step 2: Parsing
    parser = Parser(tokens)
    ast = parser.parse()

    pretty_print_ast(ast)

if __name__ == "__main__":
    main()

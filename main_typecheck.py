
import sys
from compiler.lexer_regex import RegexLexer
from compiler.parser import Parser
from compiler.scope_analyzer import analyze_scope, ScopeError
from compiler.type_checker import TypeChecker
from compiler.utils import read_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_typecheck.py <sourcefile>")
        sys.exit(1)

    src_path = sys.argv[1]

    try:
        source_code = read_file(src_path)
    except FileNotFoundError:
        print(f"Error: File '{src_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    lexer = RegexLexer(source_code)
    try:
        tokens = lexer.tokenize()
    except Exception as e:
        print(f"Lexical error: {e}")
        sys.exit(1)

    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    try:
        scope_analyzer = analyze_scope(ast)
    except ScopeError as e:
        print("Scope analysis failed:")
        print(e)
        sys.exit(1)

    type_checker = TypeChecker(scope_analyzer)
    try:
        type_checker.check_program(ast)
        print(" Type check passed! No type errors detected.")
    except Exception as e:
        print("✗ Type check failed:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

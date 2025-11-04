# main_for_all.py - Main compiler driver with scope analysis (Windows-compatible)

import sys
import os

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from compiler.lexer_noregex import NoRegexLexer
from compiler.lexer_regex import RegexLexer
from compiler.parser import Parser, pretty_print_ast
from compiler.scope_analyzer import analyze_scope, ScopeError
from compiler.utils import read_file

def compile_file(input_path: str, output_dir: str = "output", use_regex: bool = False):
    """
    Compile a source file through all stages:
    1. Lexical analysis (tokenization)
    2. Syntax analysis (parsing)
    3. Scope analysis
    """
    
    # Read source file
    try:
        source_code = read_file(input_path)
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    filename = os.path.splitext(os.path.basename(input_path))[0]
    
    print(f"\n{'='*70}")
    print(f"Compiling: {input_path}")
    print(f"{'='*70}\n")
    
    # Stage 1: Lexical Analysis
    print("[Stage 1] Lexical Analysis...")
    try:
        if use_regex:
            lexer = RegexLexer(source_code)
        else:
            lexer = NoRegexLexer(source_code)
        
        tokens = lexer.tokenize()
        print(f"✓ Tokenization successful: {len(tokens)} tokens generated")
        
        # Save tokens to file
        os.makedirs(output_dir, exist_ok=True)
        tokens_file = os.path.join(output_dir, f"{filename}_tokens.txt")
        with open(tokens_file, "w", encoding="utf-8") as f:
            for token in tokens:
                f.write(f"{token}\n")
        print(f"  Tokens saved to: {tokens_file}")
        
    except SyntaxError as e:
        print(f"✗ Lexical error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during tokenization: {e}")
        return False
    
    # Stage 2: Syntax Analysis
    print("\n[Stage 2] Syntax Analysis...")
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("✓ Parsing successful: AST generated")
        
        # Save AST to file
        ast_file = os.path.join(output_dir, f"{filename}_ast.txt")
        with open(ast_file, "w", encoding="utf-8") as f:
            # Redirect stdout to file temporarily
            old_stdout = sys.stdout
            try:
                sys.stdout = f
                pretty_print_ast(ast)
            finally:
                sys.stdout = old_stdout
        print(f"  AST saved to: {ast_file}")
        
    except Exception as e:
        print(f"✗ Parse error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Stage 3: Scope Analysis
    print("\n[Stage 3] Scope Analysis...")
    try:
        analyzer = analyze_scope(ast)
        print("✓ Scope analysis successful: No scope errors detected")
        
        # Save symbol table to file
        scope_file = os.path.join(output_dir, f"{filename}_scope.txt")
        with open(scope_file, "w", encoding="utf-8") as f:
            f.write("GLOBAL SCOPE SYMBOL TABLE\n")
            f.write("=" * 60 + "\n\n")
            
            if analyzer.global_scope.symbols:
                for name, symbol in analyzer.global_scope.symbols.items():
                    f.write(f"Symbol: {name}\n")
                    f.write(f"  Kind: {symbol.kind}\n")
                    f.write(f"  Type: {symbol.type_tok}\n")
                    if symbol.params:
                        f.write(f"  Parameters: {len(symbol.params)}\n")
                        for param in symbol.params:
                            f.write(f"    - {param.name}: {param.type_tok}\n")
                    f.write(f"  Scope Level: {symbol.scope_level}\n")
                    f.write("\n")
            else:
                f.write("(No global symbols)\n")
        
        print(f"  Symbol table saved to: {scope_file}")
        print(f"\n  Global scope contains {len(analyzer.global_scope.symbols)} symbols:")
        for name, symbol in analyzer.global_scope.symbols.items():
            if symbol.kind == 'function':
                param_count = len(symbol.params) if symbol.params else 0
                print(f"    - {name}: {symbol.kind} ({symbol.type_tok}) with {param_count} params")
            else:
                print(f"    - {name}: {symbol.kind} ({symbol.type_tok})")
        
    except ScopeError as e:
        print(f"✗ Scope analysis failed:")
        error_lines = str(e).split('\n')
        for line in error_lines:
            print(f"  {line}")
        
        # Save errors to file
        error_file = os.path.join(output_dir, f"{filename}_scope_errors.txt")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write("SCOPE ANALYSIS ERRORS\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(e))
        print(f"\n  Errors saved to: {error_file}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during scope analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n{'='*70}")
    print("✓ Compilation successful!")
    print(f"{'='*70}\n")
    return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main_for_all.py <source_file> [--regex]")
        print("\nOptions:")
        print("  --regex    Use regex-based lexer instead of manual lexer")
        print("\nExample:")
        print("  python main_for_all.py examples/valid_program.txt")
        print("  python main_for_all.py examples/valid_program.txt --regex")
        sys.exit(1)
    
    input_file = sys.argv[1]
    use_regex = "--regex" in sys.argv
    
    success = compile_file(input_file, use_regex=use_regex)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
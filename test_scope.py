# test_scope.py - Test the scope analyzer

from compiler.lexer_noregex import NoRegexLexer
from compiler.parser import Parser
from compiler.scope_analyzer import analyze_scope, ScopeError

def test_scope_analysis(code: str, description: str):
    """Test scope analysis on a code snippet"""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"{'='*60}")
    print(f"Code:\n{code}\n")
    
    try:
        # Tokenize
        lexer = NoRegexLexer(code)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Analyze scope
        analyzer = analyze_scope(ast)
        
        print("✓ Scope analysis passed - no errors detected")
        print(f"\nSymbol table (global scope):")
        for name, symbol in analyzer.global_scope.symbols.items():
            print(f"  {name}: kind={symbol.kind}, type={symbol.type_tok}")
        
    except ScopeError as e:
        print(f"✗ Scope analysis failed:")
        print(f"  {e}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Test 1: Valid program with proper scoping
    test_scope_analysis("""
function int add(int a, int b) {
    return a + b
}

function int main() {
    int x = 5
    int y = 10
    int result = add(x, y)
    return result
}
""", "Valid program with function calls")

    # Test 2: Undeclared variable
    test_scope_analysis("""
function int main() {
    int x = 5
    return y
}
""", "Undeclared variable accessed")

    # Test 3: Undefined function
    test_scope_analysis("""
function int main() {
    int x = foo(5)
    return x
}
""", "Undefined function called")

    # Test 4: Variable redefinition in same scope
    test_scope_analysis("""
function int main() {
    int x = 5
    int x = 10
    return x
}
""", "Variable redefinition in same scope")

    # Test 5: Function redefinition
    test_scope_analysis("""
function int add(int a, int b) {
    return a + b
}

function int add(int x, int y) {
    return x + y
}
""", "Function prototype redefinition")

    # Test 6: Valid shadowing (inner scope)
    test_scope_analysis("""
function int main() {
    int x = 5
    {
        int x = 10
        return x
    }
}
""", "Valid shadowing - inner scope variable")

    # Test 7: Block scope variable access
    test_scope_analysis("""
function int main() {
    {
        int x = 5
    }
    return x
}
""", "Invalid - accessing block-scoped variable outside block")

    # Test 8: For loop scope
    test_scope_analysis("""
function int main() {
    for (int i = 0; i < 10; i = i + 1) {
        int x = i * 2
    }
    return i
}
""", "Invalid - for loop variable accessed outside loop")

    # Test 9: If-else scope
    test_scope_analysis("""
function int main() {
    int x = 5
    if (x > 3) {
        int y = 10
        return y
    } else {
        int z = 20
        return z
    }
}
""", "Valid if-else with block-scoped variables")

    # Test 10: Nested functions with parameters
    test_scope_analysis("""
function int outer(int a) {
    int b = a + 5
    return b
}

function int inner(int x) {
    int y = outer(x)
    return y + x
}
""", "Valid nested function calls with parameters")

    # Test 11: Global variables
    test_scope_analysis("""
int globalVar = 100

function int useGlobal() {
    return globalVar
}

function int main() {
    int result = useGlobal()
    return result
}
""", "Valid global variable access")

    # Test 12: Parameter shadowing
    test_scope_analysis("""
function int test(int x) {
    int x = 10
    return x
}
""", "Invalid - parameter redefinition in function body")
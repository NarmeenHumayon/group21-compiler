# compiler/scope_analyzer.py
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .parser import (
    Program, FnDecl, Param, VarDecl, ExprStmt, ReturnStmt,
    IfStmt, ForStmt, BreakStmt, Binary, Unary, Literal,
    Identifier, Call
)

# Scope error types
class ScopeError(Exception):
    """Base class for scope analysis errors"""
    pass

class UndeclaredVariableAccessed(ScopeError):
    """Variable used before declaration"""
    pass

class UndefinedFunctionCalled(ScopeError):
    """Function called but not defined"""
    pass

class VariableRedefinition(ScopeError):
    """Variable declared twice in same scope"""
    pass

class FunctionPrototypeRedefinition(ScopeError):
    """Function defined twice"""
    pass


@dataclass
class Symbol:
    """Represents a symbol in the symbol table"""
    name: str
    kind: str  # 'var', 'param', 'function'
    type_tok: Optional[str] = None  # 'Int', 'Float', 'Bool', 'String'
    params: Optional[List] = None  # For functions
    scope_level: int = 0


class ScopeNode:
    """A single scope frame in the spaghetti stack"""
    def __init__(self, parent: Optional['ScopeNode'] = None, scope_type: str = 'block'):
        self.parent = parent
        self.scope_type = scope_type  # 'global', 'function', 'block'
        self.symbols: Dict[str, Symbol] = {}
        self.level = 0 if parent is None else parent.level + 1
    
    def define(self, name: str, symbol: Symbol):
        """Define a symbol in this scope"""
        if name in self.symbols:
            if symbol.kind == 'function':
                raise FunctionPrototypeRedefinition(
                    f"Function '{name}' is already defined in this scope"
                )
            else:
                raise VariableRedefinition(
                    f"Variable '{name}' is already defined in this scope"
                )
        self.symbols[name] = symbol
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol only in this scope"""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope or any parent scope"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None


class ScopeAnalyzer:
    """Performs scope analysis using a spaghetti stack"""
    
    def __init__(self):
        self.global_scope = ScopeNode(parent=None, scope_type='global')
        self.current_scope = self.global_scope
        self.errors: List[str] = []
    
    def enter_scope(self, scope_type: str = 'block'):
        """Push a new scope onto the stack"""
        self.current_scope = ScopeNode(parent=self.current_scope, scope_type=scope_type)
    
    def exit_scope(self):
        """Pop the current scope from the stack"""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent
    
    def define_symbol(self, name: str, kind: str, type_tok: Optional[str] = None, 
                     params: Optional[List] = None):
        """Define a symbol in the current scope"""
        symbol = Symbol(
            name=name,
            kind=kind,
            type_tok=type_tok,
            params=params,
            scope_level=self.current_scope.level
        )
        self.current_scope.define(name, symbol)
    
    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """Look up a symbol starting from current scope"""
        return self.current_scope.lookup(name)
    
    def analyze(self, ast: Program):
        """Main entry point for scope analysis"""
        try:
            self.visit_program(ast)
            if self.errors:
                raise ScopeError("\n".join(self.errors))
        except ScopeError:
            raise
    
    def visit_program(self, node: Program):
        """Visit the program node"""
        # First pass: collect all function declarations
        for item in node.items:
            if isinstance(item, FnDecl):
                try:
                    self.define_symbol(
                        item.name,
                        'function',
                        item.type_tok,
                        item.params
                    )
                except (FunctionPrototypeRedefinition, VariableRedefinition) as e:
                    self.errors.append(str(e))
        
        # Second pass: analyze function bodies and global statements
        for item in node.items:
            if isinstance(item, FnDecl):
                self.visit_fn_decl(item)
            elif isinstance(item, tuple) and item[0] == "Var":
                self.visit_var_decl(item[1])
            else:
                self.visit_stmt(item)
    
    def visit_fn_decl(self, node: FnDecl):
        """Visit a function declaration"""
        # Enter function scope
        self.enter_scope('function')
        
        # Add parameters to function scope
        for param in node.params:
            try:
                self.define_symbol(param.name, 'param', param.type_tok)
            except (FunctionPrototypeRedefinition, VariableRedefinition) as e:
                self.errors.append(str(e))
        
        # Visit function body
        for stmt in node.body:
            self.visit_stmt(stmt)
        
        # Exit function scope
        self.exit_scope()
    
    def visit_var_decl(self, node: VarDecl):
        """Visit a variable declaration"""
        # First analyze the initialization expression if present
        if node.expr is not None:
            self.visit_expr(node.expr)
        
        # Then define the variable in current scope
        try:
            self.define_symbol(node.name, 'var', node.type_tok)
        except (FunctionPrototypeRedefinition, VariableRedefinition) as e:
            self.errors.append(str(e))
    
    def visit_stmt(self, stmt):
        """Visit a statement"""
        if isinstance(stmt, tuple):
            if stmt[0] == "Var":
                self.visit_var_decl(stmt[1])
            elif stmt[0] == "Block":
                self.enter_scope('block')
                for s in stmt[1]:
                    self.visit_stmt(s)
                self.exit_scope()
        elif isinstance(stmt, ExprStmt):
            self.visit_expr(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            if stmt.expr is not None:
                self.visit_expr(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self.visit_expr(stmt.cond)
            # if block
            self.enter_scope('block')
            for s in stmt.if_block:
                self.visit_stmt(s)
            self.exit_scope()
            # else block
            if stmt.else_block:
                self.enter_scope('block')
                for s in stmt.else_block:
                    self.visit_stmt(s)
                self.exit_scope()
        elif isinstance(stmt, ForStmt):
            # Enter for-loop scope
            self.enter_scope('block')
            
            # Visit init (can be var decl or expr)
            if stmt.init is not None:
                if isinstance(stmt.init, VarDecl):
                    self.visit_var_decl(stmt.init)
                elif isinstance(stmt.init, ExprStmt):
                    self.visit_expr(stmt.init.expr)
            
            # Visit condition
            if stmt.cond is not None:
                self.visit_expr(stmt.cond)
            
            # Visit update
            if stmt.updt is not None:
                self.visit_expr(stmt.updt)
            
            # Visit body
            for s in stmt.block:
                self.visit_stmt(s)
            
            # Exit for-loop scope
            self.exit_scope()
        elif isinstance(stmt, BreakStmt):
            pass  # Nothing to check for break
    
    def visit_expr(self, expr):
        """Visit an expression"""
        if isinstance(expr, Binary):
            self.visit_expr(expr.left)
            self.visit_expr(expr.right)
        elif isinstance(expr, Unary):
            self.visit_expr(expr.expr)
        elif isinstance(expr, Literal):
            pass  # Literals don't need scope checking
        elif isinstance(expr, Identifier):
            # Check if variable is declared
            symbol = self.lookup_symbol(expr.name)
            if symbol is None:
                self.errors.append(
                    f"UndeclaredVariableAccessed: Variable '{expr.name}' is not declared"
                )
        elif isinstance(expr, Call):
            # Check if it's a function call
            if isinstance(expr.callee, Identifier):
                symbol = self.lookup_symbol(expr.callee.name)
                if symbol is None:
                    self.errors.append(
                        f"UndefinedFunctionCalled: Function '{expr.callee.name}' is not defined"
                    )
                elif symbol.kind != 'function':
                    # Variable used as function
                    self.errors.append(
                        f"UndefinedFunctionCalled: '{expr.callee.name}' is not a function"
                    )
            else:
                # Complex callee expression
                self.visit_expr(expr.callee)
            
            # Visit arguments
            for arg in expr.args:
                self.visit_expr(arg)


def analyze_scope(ast: Program) -> ScopeAnalyzer:
    """Convenience function to perform scope analysis"""
    analyzer = ScopeAnalyzer()
    analyzer.analyze(ast)
    return analyzer
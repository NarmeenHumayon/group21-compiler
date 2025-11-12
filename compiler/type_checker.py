
from typing import Optional, List
from .scope_analyzer import ScopeAnalyzer, ScopeNode, Symbol
from .parser import (
    Program, FnDecl, Param, VarDecl, ExprStmt, ReturnStmt,
    IfStmt, ForStmt, BreakStmt, Binary, Unary, Literal,
    Identifier, Call
)

class TypeChkError(Exception): pass
class ErroneousVarDecl(TypeChkError): pass
class FnCallParamCount(TypeChkError): pass
class FnCallParamType(TypeChkError): pass
class ErroneousReturnType(TypeChkError): pass
class ExpressionTypeMismatch(TypeChkError): pass
class ExpectedBooleanExpression(TypeChkError): pass
class ErroneousBreak(TypeChkError): pass
class NonBooleanCondStmt(TypeChkError): pass
class EmptyExpression(TypeChkError): pass
class AttemptedBoolOpOnNonBools(TypeChkError): pass
class AttemptedBitOpOnNonNumeric(TypeChkError): pass
class AttemptedShiftOnNonInt(TypeChkError): pass
class AttemptedAddOpOnNonNumeric(TypeChkError): pass
class AttemptedExponentiationOfNonNumeric(TypeChkError): pass
class ReturnStmtNotFound(TypeChkError): pass

class TypeChecker:
    def __init__(self, scope_analyzer: ScopeAnalyzer):
       
        self.scope_analyzer = scope_analyzer
        self.current_scope: ScopeNode = scope_analyzer.global_scope
        self.current_function: Optional[Symbol] = None  # track current function

    
    def check_program(self, program: Program):
        for item in program.items:
            self.check_item(item)

    def check_item(self, item):
        if isinstance(item, FnDecl):
            self.check_fn_decl(item)
        elif isinstance(item, VarDecl):
            self.check_var_decl(item)
        else:
            self.check_stmt(item)

    def check_fn_decl(self, node: FnDecl):
       
        self.current_function = self.scope_analyzer.lookup_symbol(node.name)
        self.current_scope = self.get_function_scope(node.name)
       
        for param in node.params:
            if param.type_tok is None:
                raise ErroneousVarDecl(f"Parameter '{param.name}' has no type")
     
        returned = False
        for stmt in node.body:
            if isinstance(stmt, ReturnStmt):
                returned = True
            self.check_stmt(stmt)
       
        if self.current_function.type_tok != "Void" and not returned:
            raise ReturnStmtNotFound(f"Function '{node.name}' has no return statement")
        
        self.current_scope = self.current_scope.parent
        self.current_function = None

    def check_var_decl(self, node: VarDecl):
        if node.expr is not None:
            expr_type = self.check_expr(node.expr)
            if expr_type != node.type_tok:
                raise ExpressionTypeMismatch(
                    f"Variable '{node.name}' assigned expression of type '{expr_type}', expected '{node.type_tok}'"
                )

    def check_stmt(self, stmt):
        if isinstance(stmt, ExprStmt):
            self.check_expr(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            expr_type = self.check_expr(stmt.expr) if stmt.expr else "Void"
            if expr_type != self.current_function.type_tok:
                raise ErroneousReturnType(
                    f"Return type '{expr_type}' does not match function return type '{self.current_function.type_tok}'"
                )
        elif isinstance(stmt, IfStmt):
            cond_type = self.check_expr(stmt.cond)
            if cond_type != "Bool":
                raise ExpectedBooleanExpression("If condition must be boolean")
          
            self.enter_scope('if')
            for s in stmt.if_block:
                self.check_stmt(s)
            self.exit_scope()
            if stmt.else_block:
                self.enter_scope('else')
                for s in stmt.else_block:
                    self.check_stmt(s)
                self.exit_scope()
        elif isinstance(stmt, ForStmt):
            self.enter_scope('for')
            if stmt.init:
                if isinstance(stmt.init, VarDecl):
                    self.check_var_decl(stmt.init)
                else:
                    self.check_expr(stmt.init.expr)
            if stmt.cond:
                cond_type = self.check_expr(stmt.cond)
                if cond_type != "Bool":
                    raise NonBooleanCondStmt("For loop condition must be boolean")
            if stmt.updt:
                self.check_expr(stmt.updt)
            for s in stmt.block:
                self.check_stmt(s)
            self.exit_scope()
        elif isinstance(stmt, BreakStmt):
            if not self.in_loop():
                raise ErroneousBreak("Break statement outside loop")

    def check_expr(self, expr):
        if expr is None:
            raise EmptyExpression()
        if isinstance(expr, Literal):
            return expr.type_tok
        elif isinstance(expr, Identifier):
            symbol = self.scope_analyzer.lookup_symbol(expr.name)
            if symbol is None:
                raise ExpressionTypeMismatch(f"Undeclared variable '{expr.name}'")
            return symbol.type_tok
        elif isinstance(expr, Unary):
            operand_type = self.check_expr(expr.expr)
            # TODO: add type rules per operator
            return operand_type
        elif isinstance(expr, Binary):
            left_type = self.check_expr(expr.left)
            right_type = self.check_expr(expr.right)
            op = expr.op
            if op in ["+", "-", "*", "/", "**"]:
                if left_type not in ["Int", "Float"] or right_type not in ["Int", "Float"]:
                    if op == "**":
                        raise AttemptedExponentiationOfNonNumeric()
                    else:
                        raise AttemptedAddOpOnNonNumeric()
                return left_type
            elif op in ["&&", "||"]:
                if left_type != "Bool" or right_type != "Bool":
                    raise AttemptedBoolOpOnNonBools()
                return "Bool"
            # TODO: bitwise, comparison, shift operators
            return left_type
        elif isinstance(expr, Call):
            fn_symbol = self.scope_analyzer.lookup_symbol(expr.callee.name)
            if fn_symbol is None:
                raise FnCallParamCount(f"Function '{expr.callee.name}' not defined")
           
            param_count = len(fn_symbol.params) if fn_symbol.params else 0
            if len(expr.args) != param_count:
                raise FnCallParamCount(
                    f"Function '{expr.callee.name}' expects {param_count} args, got {len(expr.args)}"
                )
           
            for arg, param in zip(expr.args, fn_symbol.params):
                arg_type = self.check_expr(arg)
                if arg_type != param.type_tok:
                    raise FnCallParamType(
                        f"Function '{expr.callee.name}' argument '{param.name}' expects '{param.type_tok}', got '{arg_type}'"
                    )
            return fn_symbol.type_tok
        return "Unknown"

    def enter_scope(self, scope_type):
        new_scope = ScopeNode(parent=self.current_scope, scope_type=scope_type)
        self.current_scope = new_scope

    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def in_loop(self):
        scope = self.current_scope
        while scope:
            if scope.scope_type == 'for':
                return True
            scope = scope.parent
        return False

    def get_function_scope(self, fn_name: str):
        for scope in self.scope_analyzer.all_scopes:
            if scope.scope_type == 'function' and scope.name == fn_name:
                return scope
        raise Exception(f"Function scope '{fn_name}' not found")

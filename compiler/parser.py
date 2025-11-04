# compiler/parser.py
from typing import List, Optional, Any
from .tokens import Token
from dataclasses import dataclass

# AST classes (simple dataclasses)
@dataclass
class Program: items: list
@dataclass
class FnDecl:
    type_tok: str; name: str; params: list; body: list
@dataclass
class Param:
    type_tok: str; name: str
@dataclass
class VarDecl:
    type_tok: str; name: str; expr: Optional[Any]
@dataclass
class ExprStmt:
    expr: Any
@dataclass
class ReturnStmt:
    expr: Optional[Any]
@dataclass
class IfStmt:
    cond: Any; if_block: list; else_block: list
@dataclass
class ForStmt:
    init: Optional[Any]; cond: Optional[Any]; updt: Optional[Any]; block: list
@dataclass
class BreakStmt: pass
@dataclass
class Binary:
    op: str; left: Any; right: Any
@dataclass
class Unary:
    op: str; expr: Any
@dataclass
class Literal:
    value: Any
@dataclass
class Identifier:
    name: str
@dataclass
class Call:
    callee: Any; args: list

# Errors
class ParseError(Exception): pass
class UnexpectedEOF(ParseError): pass
class FailedToFindToken(ParseError): pass
class ExpectedTypeToken(ParseError): pass
class ExpectedIdentifier(ParseError): pass
class UnexpectedToken(ParseError): pass
class ExpectedExpr(ParseError): pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        if self.pos >= len(self.tokens):
            return Token("EOF", None)
        return self.tokens[self.pos]

    def next(self):
        tok = self._peek()
        if tok.type == "EOF":
            raise UnexpectedEOF("Unexpected EOF")
        self.pos += 1
        return tok

    def match(self, *types):
        if self._peek().type in types:
            return self.next()
        return None

    def expect(self, ttype):
        tok = self._peek()
        if tok.type == ttype:
            return self.next()
        raise FailedToFindToken(f"Expected {ttype}, got {tok.type} at {tok.pos}")

    def parse(self):
        items = []
        while self._peek().type != "EOF":
            if self._peek().type == "Function":
                items.append(self.parse_fn_decl())
            elif self._peek().type in ("Int","Float","Bool","String"):
                var = self.parse_var_decl()
                self.match("Dot","Semicolon")
                items.append(("Var", var))
            else:
                items.append(self.parse_stmt())
        return Program(items)

    def parse_fn_decl(self):
        self.expect("Function")
        t = self._peek()
        if t.type not in ("Int","Float","Bool","String"):
            raise ExpectedTypeToken("Expected type token after Function")
        type_tok = self.next().type
        name = self.expect_identifier()
        self.expect("ParenL")
        params = []
        if self._peek().type != "ParenR":
            params.append(self.parse_param())
            while self.match("Comma"):
                params.append(self.parse_param())
        self.expect("ParenR")
        self.expect("BraceL")
        body = []
        while self._peek().type != "BraceR":
            body.append(self.parse_stmt())
        self.expect("BraceR")
        self.match("Dot","Semicolon")
        return FnDecl(type_tok,name,params,body)

    def parse_param(self):
        t = self._peek()
        if t.type not in ("Int","Float","Bool","String"):
            raise ExpectedTypeToken("Expected param type")
        type_tok = self.next().type
        name = self.expect_identifier()
        return Param(type_tok,name)

    def parse_var_decl(self):
        t=self._peek()
        if t.type not in ("Int","Float","Bool","String"):
            raise ExpectedTypeToken("Expected type token for var")
        type_tok=self.next().type
        name=self.expect_identifier()
        expr=None
        if self.match("AssignOp"):
            expr=self.parse_expr()
        return VarDecl(type_tok,name,expr)

    def expect_identifier(self):
        tok=self._peek()
        if tok.type=="Identifier":
            return self.next().value
        raise ExpectedIdentifier(f"Expected identifier at {tok.pos}")

    def parse_stmt(self):
        tok=self._peek()
        if tok.type in ("Int","Float","Bool","String"):
            var=self.parse_var_decl()
            self.match("Dot","Semicolon")
            return ("Var",var)
        if tok.type=="Return" or tok.type=="wapsi":
            self.next()
            if self._peek().type in ("Dot","Semicolon"):
                self.match("Dot","Semicolon"); return ReturnStmt(None)
            expr=self.parse_expr()
            self.match("Dot","Semicolon")
            return ReturnStmt(expr)
        if tok.type=="If" or tok.type=="agar":
            return self.parse_if()
        if tok.type=="For" or tok.type=="duhrao":
            return self.parse_for()
        if tok.type=="Break" or tok.type=="toro":
            self.next()
            self.match("Dot","Semicolon")
            return BreakStmt()
        if tok.type=="BraceL":
            self.next()
            block=[]
            while self._peek().type!="BraceR":
                block.append(self.parse_stmt())
            self.expect("BraceR")
            self.match("Dot","Semicolon")
            return ("Block", block)
        expr=self.parse_expr()
        self.match("Dot","Semicolon")
        return ExprStmt(expr)

    def parse_if(self):
        self.next()
        self.expect("ParenL")
        cond=self.parse_expr()
        self.expect("ParenR")
        self.expect("BraceL")
        if_block=[]
        while self._peek().type!="BraceR":
            if_block.append(self.parse_stmt())
        self.expect("BraceR")
        else_block=[]
        if self.match("Else") or self.match("warna"):
            self.expect("BraceL")
            while self._peek().type!="BraceR":
                else_block.append(self.parse_stmt())
            self.expect("BraceR")
        self.match("Dot","Semicolon")
        return IfStmt(cond, if_block, else_block)

    def parse_for(self):
        self.next()
        self.expect("ParenL")
        init=None
        if self._peek().type in ("Int","Float","Bool","String"):
            init=self.parse_var_decl()
            self.match("Dot","Semicolon")
        elif self._peek().type!="Dot":
            init_exp=self.parse_expr()
            init=ExprStmt(init_exp)
            self.match("Dot","Semicolon")
        else:
            self.match("Dot","Semicolon")
        cond=None
        if self._peek().type!="Dot":
            cond=self.parse_expr()
        self.match("Dot","Semicolon")
        updt=None
        if self._peek().type!="ParenR":
            updt=self.parse_expr()
        self.expect("ParenR")
        self.expect("BraceL")
        block=[]
        while self._peek().type!="BraceR":
            block.append(self.parse_stmt())
        self.expect("BraceR")
        self.match("Dot","Semicolon")
        return ForStmt(init,cond,updt,block)

    # expressions (precedence climbing)
    def parse_expr(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left=self.parse_logical_or()
        if self.match("AssignOp"):
            right=self.parse_assignment()
            if isinstance(left, Identifier):
                return Binary("AssignOp", left, right)
            raise UnexpectedToken("Left side of assignment must be identifier")
        return left

    def parse_logical_or(self):
        node=self.parse_logical_and()
        while self.match("OrOp"):
            right=self.parse_logical_and(); node=Binary("OrOp",node,right)
        return node

    def parse_logical_and(self):
        node=self.parse_equality()
        while self.match("AndOp"):
            right=self.parse_equality(); node=Binary("AndOp",node,right)
        return node

    def parse_equality(self):
        node=self.parse_comparison()
        while True:
            if self.match("EqualsOp"):
                right=self.parse_comparison(); node=Binary("EqualsOp",node,right)
            elif self.match("NotEquals"):
                right=self.parse_comparison(); node=Binary("NotEquals",node,right)
            else:
                break
        return node

    def parse_comparison(self):
        node=self.parse_add()
        while True:
            if self.match("LessThan"):
                right=self.parse_add(); node=Binary("LessThan",node,right)
            elif self.match("GreaterThan"):
                right=self.parse_add(); node=Binary("GreaterThan",node,right)
            elif self.match("LessEq"):
                right=self.parse_add(); node=Binary("LessEq",node,right)
            elif self.match("GreaterEq"):
                right=self.parse_add(); node=Binary("GreaterEq",node,right)
            else:
                break
        return node

    def parse_add(self):
        node=self.parse_mul()
        while True:
            if self.match("AddOp"):
                right=self.parse_mul(); node=Binary("AddOp",node,right)
            elif self.match("SubOp"):
                right=self.parse_mul(); node=Binary("SubOp",node,right)
            else:
                break
        return node

    def parse_mul(self):
        node=self.parse_unary()
        while True:
            if self.match("MulOp"):
                right=self.parse_unary(); node=Binary("MulOp",node,right)
            elif self.match("DivOp"):
                right=self.parse_unary(); node=Binary("DivOp",node,right)
            elif self.match("ModOp"):
                right=self.parse_unary(); node=Binary("ModOp",node,right)
            else:
                break
        return node

    def parse_unary(self):
        if self.match("SubOp"):
            node=self.parse_unary(); return Unary("SubOp", node)
        if self.match("NotOp"):
            node=self.parse_unary(); return Unary("NotOp", node)
        return self.parse_call()

    def parse_call(self):
        node=self.parse_primary()
        while True:
            if self.match("ParenL"):
                args=[]
                if self._peek().type!="ParenR":
                    args.append(self.parse_expr())
                    while self.match("Comma"):
                        args.append(self.parse_expr())
                self.expect("ParenR")
                node=Call(node,args)
            else:
                break
        return node

    def parse_primary(self):
        tok=self._peek()
        if tok.type=="IntLit":
            val=self.next().value; return Literal(val)
        if tok.type=="FloatLit":
            val=self.next().value; return Literal(val)
        if tok.type=="StringLit":
            val=self.next().value; return Literal(val)
        if tok.type=="BoolLit":
            val=self.next().value; return Literal(val)
        if tok.type=="Identifier":
            name=self.next().value; return Identifier(name)
        if tok.type=="ParenL":
            self.next(); node=self.parse_expr(); self.expect("ParenR"); return node
        raise ExpectedExpr(f"Expected primary expression, got {tok.type} at {tok.pos}")

# --------------------------------------------------------------------
# Helper to pretty-print the AST (for debugging / assignment output)
# --------------------------------------------------------------------
# Replace the pretty_print_ast function in compiler/parser.py with this:

def pretty_print_ast(node, indent: int = 0):
    """Recursively print AST nodes with indentation (Windows-compatible)."""
    space = "  " * indent

    # Handle lists of nodes
    if isinstance(node, list):
        for item in node:
            pretty_print_ast(item, indent)
        return

    # Handle tuples (like ("Var", VarDecl(...)))
    if isinstance(node, tuple):
        print(f"{space}Tuple:")
        for i, item in enumerate(node):
            print(f"{space}  [{i}]:")
            pretty_print_ast(item, indent + 2)
        return

    # Handle our dataclass AST nodes
    if hasattr(node, "__dataclass_fields__"):
        print(f"{space}{node.__class__.__name__}")
        for field in node.__dataclass_fields__:
            value = getattr(node, field)
            # Use ASCII characters instead of Unicode box-drawing chars
            print(f"{space}  |-- {field}:")
            pretty_print_ast(value, indent + 2)
        return

    # Handle primitive values (str, int, None, etc.)
    print(f"{space}{repr(node)}")
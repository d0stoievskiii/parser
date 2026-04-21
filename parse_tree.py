from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Union

EPSILON = "ε"

class TokenType(Enum):
    LPAREN = auto()
    RPAREN = auto()
    QUOTE = auto()

    DEFINE = auto()
    IF = auto()
    LAMBDA = auto()
    LET = auto()

    IDENT = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()

    EOF = auto()

class NonTerminal(Enum):
    PROGRAM = auto()
    EXPR_SEQ = auto()
    EXPR = auto()
    ATOM = auto()
    QUOTE_EXPR = auto()
    LIST_EXPR = auto()
    LIST_CONTENTS = auto()
    DEFINE_TAIL = auto()
    APP_TAIL = auto()
    PARAM_LIST = auto()
    BODY = auto()
    BODY_TAIL = auto()
    BINDING_SEQ = auto()
    BINDING = auto()

name_to_tokenType_map = dict()
for t in TokenType:
    name_to_tokenType_map[t.name] = t

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int


@dataclass
class ParseTreeNode:
    symbol: Union[TokenType, NonTerminal, str]
    children: list["ParseTreeNode"] = field(default_factory=list)
    token: Optional[Token] = None

@dataclass
class Production:
    lhs: NonTerminal
    rhs: list[Union[TokenType, NonTerminal, str]]
    index: int = -1

PRODUCTIONS = [
    # 1. Program -> ExprSeq EOF
    Production(
        lhs=NonTerminal.PROGRAM,
        rhs=[NonTerminal.EXPR_SEQ, TokenType.EOF],
        index=1,
    ),

    # 2. ExprSeq -> Expr ExprSeq
    Production(
        lhs=NonTerminal.EXPR_SEQ,
        rhs=[NonTerminal.EXPR, NonTerminal.EXPR_SEQ],
        index=2,
    ),

    # 3. ExprSeq -> ε
    Production(
        lhs=NonTerminal.EXPR_SEQ,
        rhs=[EPSILON],
        index=3,
    ),

    # 4. Expr -> Atom
    Production(
        lhs=NonTerminal.EXPR,
        rhs=[NonTerminal.ATOM],
        index=4,
    ),

    # 5. Expr -> QuoteExpr
    Production(
        lhs=NonTerminal.EXPR,
        rhs=[NonTerminal.QUOTE_EXPR],
        index=5,
    ),

    # 6. Expr -> ListExpr
    Production(
        lhs=NonTerminal.EXPR,
        rhs=[NonTerminal.LIST_EXPR],
        index=6,
    ),

    # 7. Atom -> IDENT
    Production(
        lhs=NonTerminal.ATOM,
        rhs=[TokenType.IDENT],
        index=7,
    ),

    # 8. Atom -> NUMBER
    Production(
        lhs=NonTerminal.ATOM,
        rhs=[TokenType.NUMBER],
        index=8,
    ),

    # 9. Atom -> BOOLEAN
    Production(
        lhs=NonTerminal.ATOM,
        rhs=[TokenType.BOOLEAN],
        index=9,
    ),

    # 10. Atom -> STRING
    Production(
        lhs=NonTerminal.ATOM,
        rhs=[TokenType.STRING],
        index=10,
    ),

    # 11. QuoteExpr -> QUOTE Expr
    Production(
        lhs=NonTerminal.QUOTE_EXPR,
        rhs=[TokenType.QUOTE, NonTerminal.EXPR],
        index=11,
    ),

    # 12. ListExpr -> LPAREN ListContents RPAREN
    Production(
        lhs=NonTerminal.LIST_EXPR,
        rhs=[TokenType.LPAREN, NonTerminal.LIST_CONTENTS, TokenType.RPAREN],
        index=12,
    ),

    # 13. ListContents -> DEFINE DefineTail
    Production(
        lhs=NonTerminal.LIST_CONTENTS,
        rhs=[TokenType.DEFINE, NonTerminal.DEFINE_TAIL],
        index=13,
    ),

    # 14. ListContents -> IF Expr Expr Expr
    Production(
        lhs=NonTerminal.LIST_CONTENTS,
        rhs=[TokenType.IF, NonTerminal.EXPR, NonTerminal.EXPR, NonTerminal.EXPR],
        index=14,
    ),

    # 15. ListContents -> LAMBDA LPAREN ParamList RPAREN Body
    Production(
        lhs=NonTerminal.LIST_CONTENTS,
        rhs=[
            TokenType.LAMBDA,
            TokenType.LPAREN,
            NonTerminal.PARAM_LIST,
            TokenType.RPAREN,
            NonTerminal.BODY,
        ],
        index=15,
    ),

    # 16. ListContents -> LET LPAREN BindingSeq RPAREN Body
    Production(
        lhs=NonTerminal.LIST_CONTENTS,
        rhs=[
            TokenType.LET,
            TokenType.LPAREN,
            NonTerminal.BINDING_SEQ,
            TokenType.RPAREN,
            NonTerminal.BODY,
        ],
        index=16,
    ),

    # 17. ListContents -> AppTail
    Production(
        lhs=NonTerminal.LIST_CONTENTS,
        rhs=[NonTerminal.APP_TAIL],
        index=17,
    ),

    # 18. DefineTail -> IDENT Expr
    Production(
        lhs=NonTerminal.DEFINE_TAIL,
        rhs=[TokenType.IDENT, NonTerminal.EXPR],
        index=18,
    ),

    # 19. DefineTail -> LPAREN IDENT ParamList RPAREN Body
    Production(
        lhs=NonTerminal.DEFINE_TAIL,
        rhs=[
            TokenType.LPAREN,
            TokenType.IDENT,
            NonTerminal.PARAM_LIST,
            TokenType.RPAREN,
            NonTerminal.BODY,
        ],
        index=19,
    ),

    # 20. AppTail -> Expr ExprSeq
    Production(
        lhs=NonTerminal.APP_TAIL,
        rhs=[NonTerminal.EXPR, NonTerminal.EXPR_SEQ],
        index=20,
    ),

    # 21. ParamList -> IDENT ParamList
    Production(
        lhs=NonTerminal.PARAM_LIST,
        rhs=[TokenType.IDENT, NonTerminal.PARAM_LIST],
        index=21,
    ),

    # 22. ParamList -> ε
    Production(
        lhs=NonTerminal.PARAM_LIST,
        rhs=[EPSILON],
        index=22,
    ),

    # 23. Body -> Expr BodyTail
    Production(
        lhs=NonTerminal.BODY,
        rhs=[NonTerminal.EXPR, NonTerminal.BODY_TAIL],
        index=23,
    ),

    # 24. BodyTail -> Expr BodyTail
    Production(
        lhs=NonTerminal.BODY_TAIL,
        rhs=[NonTerminal.EXPR, NonTerminal.BODY_TAIL],
        index=24,
    ),

    # 25. BodyTail -> ε
    Production(
        lhs=NonTerminal.BODY_TAIL,
        rhs=[EPSILON],
        index=25,
    ),

    # 26. BindingSeq -> Binding BindingSeq
    Production(
        lhs=NonTerminal.BINDING_SEQ,
        rhs=[NonTerminal.BINDING, NonTerminal.BINDING_SEQ],
        index=26,
    ),

    # 27. BindingSeq -> ε
    Production(
        lhs=NonTerminal.BINDING_SEQ,
        rhs=[EPSILON],
        index=27,
    ),

    # 28. Binding -> LPAREN IDENT Expr RPAREN
    Production(
        lhs=NonTerminal.BINDING,
        rhs=[TokenType.LPAREN, TokenType.IDENT, NonTerminal.EXPR, TokenType.RPAREN],
        index=28,
    ),
]

def symbol_to_string(symbol):
    if symbol == EPSILON:
        return "ε"
    if hasattr(symbol, "name"):  # é Enum
        return symbol.name
    return str(symbol)

def node_label(node):
    base = symbol_to_string(node.symbol)

    if node.token is not None:
        return f"{base}({node.token.lexeme!r})"

    return base

def print_tree(node, prefix="", is_last=True, file=None):
    connector = "└── " if is_last else "├── "

    print(prefix + connector + node_label(node), file=file)

    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_tree(child, new_prefix, is_last_child, file=file)

def parse_tree_to_dict(node):
    result = {
        "symbol": symbol_to_string(node.symbol),
        "children": [parse_tree_to_dict(child) for child in node.children]
    }

    if node.token is not None:
        result["token"] = {
            "type": node.token.type.name,
            "lexeme": node.token.lexeme,
            "line": node.token.line,
            "column": node.token.column
        }

    return result


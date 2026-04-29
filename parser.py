from grammar import *

TOKEN_PRETTY = {
    TokenType.LPAREN: "(",
    TokenType.RPAREN: ")",
    TokenType.QUOTE: "'",

    TokenType.DEFINE: "define",
    TokenType.IF: "if",
    TokenType.LAMBDA: "lambda",
    TokenType.LET: "let",

    TokenType.IDENT: "identificador",
    TokenType.NUMBER: "número",
    TokenType.BOOLEAN: "#t ou #f",
    TokenType.STRING: "string",

    TokenType.EOF: "fim de arquivo",
}

def pretty_token(token_type, token=None):
    if token is not None:
        if token_type in {TokenType.IDENT, TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN}:
            return repr(token.lexeme)

    return TOKEN_PRETTY.get(token_type, token_type.name)

class ParseError(Exception):
    pass

class PredictiveParser:
    def __init__(self, tokens, parsing_table, start_symbol, sync_sets=None, include_epsilon=True):
        self.tokens = tokens
        self.table = parsing_table
        self.start_symbol = start_symbol
        self.include_epsilon = include_epsilon
        self.sync_sets = sync_sets or {}
        self.pos = 0
        self.errors = []

    def _report_error(self, message):
        self.errors.append(message)
        print(message)

    def _panic(self, nonterminal):
        sync = self.sync_sets.get(nonterminal, {TokenType.EOF})

        while self.pos < len(self.tokens):
            tok = self.current_token()
            if tok.type in sync or tok.type == TokenType.EOF:
                return
            self.advance()

    def current_token(self):
        if self.pos >= len(self.tokens):
            raise ParseError("Parser foi além da stream de tokens")
        return self.tokens[self.pos]

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def _match_terminal(self, expected_type, current_token, current_node):
        if expected_type != current_token.type:
            self._report_error(
            f"Esperava {pretty_token(expected_type)}, recebeu {pretty_token(current_token.type, current_token)} "
            f"@ linha {current_token.line}, coluna {current_token.column} "
            f"perto de {current_token.lexeme!r}")
            
            if expected_type in {TokenType.RPAREN, TokenType.EOF}:
                # assumimos que foi esquecido e não descartamos o atual, que pode ser bom
                return
            else:
                # discartamos o token ruim
                self.advance()
                return

        current_node.token = current_token
        self.advance()

    def _expand_nonterminal(self, nonterminal, current_token, current_node, stack, node_stack):
        key = (nonterminal, current_token.type)
        production = self.table.get(key)

        if production is None:
            self._report_error(
            f"Nenhuma produção para {nonterminal.name} com lookahead "
            f"{current_token.type.name} @ linha {current_token.line}, "
            f"coluna {current_token.column} perto de {current_token.lexeme!r}")
            self._panic(nonterminal)
            return
        
        if production.rhs == [EPSILON]:
            if self.include_epsilon:
                epsilon_node = ParseTreeNode(EPSILON)
                current_node.children.append(epsilon_node)
            return

        children = [ParseTreeNode(symbol) for symbol in production.rhs]
        current_node.children.extend(children)

        for symbol, child in zip(reversed(production.rhs), reversed(children)):
            stack.append(symbol)
            node_stack.append(child)

    def parse(self):
        stack = [self.start_symbol]

        root = ParseTreeNode(self.start_symbol)
        node_stack = [root]

        while stack:
            if self.pos >= len(self.tokens):
                raise ParseError("Fim inesperado da entrada")
            top = stack.pop()
            current = self.current_token()
            current_node = node_stack.pop()

            if isinstance(top, TokenType):
                self._match_terminal(top, current, current_node)

            elif isinstance(top, NonTerminal):
                self._expand_nonterminal(top, current, current_node, stack, node_stack)

            else:
                raise ParseError(f"Simbolo desconhecido na pilha: {top!r}")

        if self.pos != len(self.tokens):
            tok = self.current_token()
            raise ParseError(
                f"Token inesperado à direita @ linha {tok.line}, coluna {tok.column}: "
                f"{tok.type.name} ({tok.lexeme!r})"
            )

        return root
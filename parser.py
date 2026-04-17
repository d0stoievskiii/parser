from parse_tree import *

class ParseError(Exception):
    pass

class PredictiveParser:
    def __init__(self, tokens, parsing_table, start_symbol, include_epsilon=True):
        self.tokens = tokens
        self.table = parsing_table
        self.start_symbol = start_symbol
        self.include_epsilon = include_epsilon
        self.pos = 0

    def current_token(self):
        if self.pos >= len(self.tokens):
            raise ParseError("Parser foi além da stream de tokens")
        return self.tokens[self.pos]

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def _match_terminal(self, expected_type, current_token, current_node):
        if expected_type != current_token.type:
            raise ParseError(
                f"Esperava {expected_type.name}, recebeu {current_token.type.name} "
                f"@ linha {current_token.line}, columa {current_token.column} "
                f"perto de {current_token.lexeme!r}"
            )

        current_node.token = current_token
        self.advance()

    def _expand_nonterminal(self, nonterminal, current_token, current_node, stack, node_stack):
        key = (nonterminal, current_token.type)
        production = self.table.get(key)

        if production is None:
            raise ParseError(
                f"Nenhuma produção para {nonterminal.name} com lookahead 1"
                f"{current_token.type.name} @ linha {current_token.line}, "
                f"coluna {current_token.column} perto de {current_token.lexeme!r}"
            )

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
        stack = [TokenType.EOF, self.start_symbol]

        eof_node = ParseTreeNode(TokenType.EOF)
        root = ParseTreeNode(self.start_symbol)
        node_stack = [eof_node, root]

        while stack:
            top = stack.pop()
            current = self.current_token()
            current_node = node_stack.pop()

            if top == EPSILON:
                if self.include_epsilon:
                    current_node.symbol = EPSILON
                continue

            if isinstance(top, TokenType):
                self._match_terminal(top, current, current_node)

            elif isinstance(top, NonTerminal):
                self._expand_nonterminal(top, current, current_node, stack, node_stack)

            else:
                raise ParseError(f"Simbolo desconhecido na pilha: {top!r}")

        if self.current_token().type != TokenType.EOF:
            tok = self.current_token()
            raise ParseError(
                f"Token inesperado à direita @ linha {tok.line}, coluna {tok.column}: "
                f"{tok.type.name} ({tok.lexeme!r})"
            )

        return root
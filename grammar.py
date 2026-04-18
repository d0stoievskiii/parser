from collections import defaultdict
from parse_tree import *

class Grammar:
    def __init__(self, productions, start_symbol):
        self.productions = productions
        self.start_symbol = start_symbol
        self.by_lhs = defaultdict(list)

        for p in productions:
            self.by_lhs[p.lhs].append(p)

    def get(self, non_terminal: NonTerminal):
        return self.by_lhs.get(non_terminal, [])
    

def compute_first(grammar):
    FIRST = defaultdict(set)

    # If X is a terminal, then FIRST(X) = {X}.
    for t in TokenType:
        FIRST[t].add(t)

    FIRST[EPSILON].add(EPSILON)

    changed = True

    while changed:
        changed = False

        for prod in grammar.productions:
            lhs = prod.lhs
            rhs = prod.rhs

            before = len(FIRST[lhs])

            # produção A -> ε
            if rhs == [EPSILON]:
                FIRST[lhs].add(EPSILON)
            else:
                # produção A -> Y1 Y2 ... Yk

                for symbol in rhs:
                    FIRST[lhs] |= (FIRST[symbol] - {EPSILON})

                    if EPSILON not in FIRST[symbol]:
                        break
                else:
                    # todos geram epsilon
                    FIRST[lhs].add(EPSILON)

            if len(FIRST[lhs]) > before:
                changed = True


def compute_follow(grammar, FIRST, start_symbol):
    FOLLOW = defaultdict(set)

    FOLLOW[start_symbol].add(TokenType.EOF)

    changed = True

    while(changed):
        changed = False

        for prod in grammar.productions:
            lhs = prod.lhs
            rhs = prod.rhs

            for i, B in enumerate(rhs):
                if not isinstance(B, NonTerminal):
                    continue

                before = len(FOLLOW[B])

                # resto da produção
                beta = rhs[i+1:]

                if beta:
                    first_beta = set()

                    for symbol in beta:
                        first_beta |= (FIRST[symbol] - {EPSILON})

                        if EPSILON not in FIRST[symbol]:
                            break
                    else:
                        first_beta.add(EPSILON)
                    
                    FOLLOW[B] |= (first_beta - {EPSILON})

                    if EPSILON in first_beta:
                        FOLLOW[B] |= FOLLOW[lhs]

                else:
                    # B é o último
                    FOLLOW[B] |= FOLLOW[lhs]
                
                if len(FOLLOW[B]) > before:
                    changed = True

    return FOLLOW

def build_parsing_table(grammar, FIRST, FOLLOW):
    # todo
    pass
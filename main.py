from parser import *
from grammar import *
from tokens import fetch_token_list, dump_table, save_parse_tree_json

def main():
    grammar = Grammar(PRODUCTIONS, NonTerminal.PROGRAM)
    first = compute_first(grammar)
    follow = compute_follow(grammar, first, NonTerminal.PROGRAM)
    table = build_parsing_table(grammar, first, follow)
    parser = PredictiveParser(
    tokens=fetch_token_list("token_list.json"),
    parsing_table=table,
    start_symbol=NonTerminal.PROGRAM,
    include_epsilon=True)

    tree = parser.parse()
    save_parse_tree_json(tree, "parse_tree.json")
    
    with open("tree.txt", "w", encoding="utf-8") as f:
        print_tree(tree, file=f)


if __name__ == "__main__":
    main()
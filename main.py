from parser import *
from grammar import *
from tokens import fetch_token_list, dump_table, save_parse_tree_json
from pathlib import Path

def main():
    grammar = Grammar(PRODUCTIONS, NonTerminal.PROGRAM)
    first = compute_first(grammar)
    follow = compute_follow(grammar, first, NonTerminal.PROGRAM)
    table = build_parsing_table(grammar, first, follow)

    token_dir = Path("../token_lists")
    tree_dir = Path("../trees")
    tree_dir.mkdir(parents=True, exist_ok=True)

    for token_file in sorted(token_dir.glob("*.json")):
        print(f"Parsing {token_file}...")

        parser = PredictiveParser(
            tokens=fetch_token_list(str(token_file)),
            parsing_table=table,
            start_symbol=NonTerminal.PROGRAM,
            include_epsilon=True
        )

        tree = parser.parse()

        json_output = tree_dir / f"{token_file.stem}.json"
        txt_output = tree_dir / f"{token_file.stem}.txt"

        save_parse_tree_json(tree, str(json_output))

        with open(txt_output, "w", encoding="utf-8") as f:
            print_tree(tree, file=f)

        print(f"Generated {json_output} and {txt_output}")


if __name__ == "__main__":
    main()

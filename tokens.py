from parse_tree import *
import json

def fetch_token_list(path):
    with open(path, 'r') as file:
        data = json.load(file)

    tokens = []
    for t in data["tokens"]:
        if (t["token"] == "SYMBOL" or t["token"] == "DISPLAY"):
            t["token"] = "IDENT"
        tok = name_to_tokenType_map[t["token"]]
        lexeme = t["lexeme"]
        line = t["line"]
        column = t["column"]
        tokens.append(Token(tok, lexeme, line, column))
    #scanner não adiciona EOF
    tokens.append(Token(TokenType.EOF, "", line, column+len(lexeme)))

    return tokens


def save_parse_tree_json(root, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            parse_tree_to_dict(root),
            f,
            indent=2,
            ensure_ascii=False
        )


def dump_table(table):
    with open("data.json", "w") as f:
        json.dump(table, f)
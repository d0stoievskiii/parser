from parse_tree import *
import json

def fetch_token_list(path):
    with open(path, 'r') as file:
        data = json.load(file)

    tokens = []
    for t in data["tokens"]:
        tok = name_to_tokenType_map[t["token"]]
        lexeme = t["lexeme"]
        line = t["line"]
        column = t["column"]
        tokens.append(Token(tok, lexeme, line, column))

    return tokens

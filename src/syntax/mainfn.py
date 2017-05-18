
from plex import *

def start_action(scanner, text):
    scanner.write("int main() {")

def end_action(scanner, text):
    scanner.write("return 0;\n}")

def apply(scanner):
    scanner.add_lexeme({
        "token": "mainfn_start",
        "pattern": Str("ALPHA") + Rep1(Str(" ", "\t")) + Str(":time:"),
        "action": start_action
    })

    scanner.add_lexeme({
        "token": "mainfn_end",
        "pattern": Str("OMEGA") + Rep1(Str(" ", "\t")) + Str(":time:"),
        "action": end_action
    })

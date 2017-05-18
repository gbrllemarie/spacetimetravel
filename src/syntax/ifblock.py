
from plex import *

def start_action(scanner, text):
    scanner.write("if (")
    scanner.begin("if_condition_state")

def condition_expr_action(scanner, text):
    text = text.replace(":", "")
    text = text.replace("?=", "==")
    text = text.replace("?&", "&&")
    text = text.replace("?|", "||")
    text = text.replace("?", "")
    scanner.write(text)

def condition_end_action(scanner, text):
    scanner.write(") {")
    scanner.begin("")

def end_action(scanner, text):
    scanner.write("}")

def apply(scanner):
    ws = Rep(Any(" \t"))
    if_start = Str("start") + ws + Str("check") + ws + Str("(") + ws
    if_end = Str("end") + ws + Str("check")

    var = Str(":") + Range("AZaz") + Rep(Range("AZaz09")) + Str(":")
    str_literal = Str("\"") + Rep(Rep(AnyBut("\\") + Str("\\")) + AnyBut("\"")) + Str("\"")
    num = Opt(Str("-")) + Rep(Range("09")) + Opt(Str(".") + Rep(Range("09")))
    name = (var | str_literal | num)
    operator = Str("+", "-", "/", "*", "%", "?=", "?!=", "?>", "?<", "?>=", "?<=", "?&", "&", "?|", "|")
    expression = ws + name + ws + Rep(name + ws + operator + ws)

    scanner.add_lexeme({
        "token": "if_start",
        "pattern": if_start,
        "action": start_action
    })

    scanner.add_lexeme({
        "token": "if_end",
        "pattern": if_end,
        "action": end_action
    })

    scanner.add_state("if_condition_state", [{
        "token": "if_condition_state_expr",
        "pattern": ws + expression + ws,
        "action": condition_expr_action
    }, {
        "token": "if_condition_state_end",
        "pattern": Str(")"),
        "action": condition_end_action
    }])

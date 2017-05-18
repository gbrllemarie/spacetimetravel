
from plex import *

def start_action(scanner, text):
    scanner.write("for (")
    scanner.begin("for_condition_state")

def condition_since_action(scanner, text):
    text = text.replace("since", "")
    text = text.replace(":", "")
    text = text.replace("?=", "==")
    text = text.replace("?", "")
    text = text.replace("<-", "=")
    scanner.write(text + ";")

def condition_until_action(scanner, text):
    text = text.replace("until", "")
    text = text.replace(":", "")
    text = text.replace("?=", "==")
    text = text.replace("?", "")
    text = text.replace("<-", "=")
    scanner.write(text + ";")

def condition_do_action(scanner, text):
    text = text.replace("do", "")
    text = text.replace(":", "")
    text = text.replace("?=", "==")
    text = text.replace("?", "")
    text = text.replace("<-", "=")
    scanner.write(text)

def condition_end_action(scanner, text):
    scanner.write(") {")
    scanner.begin("")

def end_action(scanner, text):
    scanner.write("}")

def apply(scanner):
    ws = Rep(Any(" \t"))
    for_start = Str("start") + ws + Str("loop") + ws + Str("(") + ws
    for_end = Str("end") + ws + Str("loop")

    var = Str(":") + Range("AZaz") + Rep(Range("AZaz09")) + Str(":")
    str_literal = Str("\"") + Rep(Rep(AnyBut("\\") + Str("\\")) + AnyBut("\"")) + Str("\"")
    num = Opt(Str("-")) + Rep(Range("09")) + Opt(Str(".") + Rep(Range("09")))
    name = (var | str_literal | num)
    operator = Str("+", "-", "/", "*", "%", "?=", "?!=", "?>", "?<", "?>=", "?<=", "<-")
    expression = ws + name + Rep(ws + operator + ws + name)

    scanner.add_lexeme({
        "token": "for_start",
        "pattern": for_start,
        "action": start_action
    })

    scanner.add_lexeme({
        "token": "for_end",
        "pattern": for_end,
        "action": end_action
    })

    scanner.add_state("for_condition_state", [{
        "token": "for_condition_state_since",
        "pattern": Str("since") + ws + expression + ws,
        "action": condition_since_action
    }, {
        "token": "for_condition_state_until",
        "pattern": Str("until") + ws + expression + ws,
        "action": condition_until_action
    }, {
        "token": "for_condition_state_do",
        "pattern": Str("do") + ws + expression + ws,
        "action": condition_do_action
    }, {
        "token": "for_condition_state_end",
        "pattern": Str(")"),
        "action": condition_end_action
    }])

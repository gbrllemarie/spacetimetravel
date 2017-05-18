
from plex import *

def def_action(scanner, text):
    datatypes = {
        "numeral": "int",
        "decimal": "float",
        "star": "char",
        "constellation": "char*",
        "day": "bool",
    }

    datatype, whitespace, name = text.partition(" ")

    datatype = datatypes.get(datatype)
    name = name.replace(":", "")

    scanner.write(datatype + whitespace + name + ";")

def set_action(scanner, text):
    text = text.replace(":", "")
    text = text.replace("<-", "=")
    scanner.write(text)
    scanner.begin("variables_set_state")

def set_state_warp_action(scanner, text):
    text = text.replace("warp(", "")
    text = text.replace(")", "", 1)
    text = text.replace(":", "")
    scanner.write(text)

def set_state_any_action(scanner, text):
    scanner.write(text)

def set_state_end_action(scanner, text):
    scanner.write(";")
    scanner.begin("")

def apply(scanner):
    datatypes = [
        "numeral",
        "decimal",
        "star",
        "constellation",
        "day"
    ]

    ws = Rep(Any(" \t"))
    name = Str(":") + Range("AZaz") + Rep(Range("AZaz09")) + Str(":")

    definition = Str(*datatypes) + ws + name
    set_value = name + ws + Str("<-") + ws
    warp_pattern = Str("warp(") + name + Str(")") + Opt(Str("(") + name + Str(")"))

    # define and initialize
    # -- todo

    # definition
    scanner.add_lexeme({
        "token": "variables_def",
        "pattern": definition,
        "action": def_action
    })

    # set value
    scanner.add_lexeme({
        "token": "variables_set",
        "pattern": set_value,
        "action": set_action
    })

    # variable setting state
    scanner.add_state("variables_set_state", [{
        "token": "variables_set_state_warp",
        "pattern": warp_pattern,
        "action": set_state_warp_action
    }, {
        "token": "variables_set_state_any",
        "pattern": Rep(AnyBut("\n")),
        "action": set_state_any_action
    }, {
        "token": "variables_set_state_end",
        "pattern": Eol,
        "action": set_state_end_action
    }])

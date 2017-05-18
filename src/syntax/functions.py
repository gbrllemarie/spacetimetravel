
from plex import *
import re

def start_action(scanner, text):
    datatypes = {
        "numeral": "int",
        "decimal": "float",
        "star": "char",
        "constellation": "char*",
        "day": "bool",
    }

    name = re.search(r"activate[ \t]+:([A-Za-z][A-Za-z0-9]+):", text).group(1)
    returntype = datatypes.get( re.search(r"returns ([A-Za-z]+)", text).group(1) )
    params = re.search(r"with[ \t]*\([ \t]*([A-Za-z0-9 \t:,]*)[ \t]*\)", text)
    if params:
        params = params.group(1)
        params = params.replace("numeral", "int")
        params = params.replace("decimal", "float")
        params = params.replace("star", "char")
        params = params.replace("constellation", "char*")
        params = params.replace("day", "bool")
        params = params.replace(":", "")
    else:
        params = ""
    scanner.write(returntype + " " + name + "(" + params + ") {")

def end_action(scanner, text):
    scanner.write("}")

def call_action(scanner, text):
    scanner.write(text)

def apply(scanner):
    ws = Rep(Any(" \t"))
    datatypes = [
        "numeral",
        "decimal",
        "star",
        "constellation",
        "day"
    ]

    var = Str(":") + Range("AZaz") + Rep(Range("AZaz09")) + Str(":")
    str_literal = Str("\"") + Rep(Rep(AnyBut("\\") + Str("\\")) + AnyBut("\"")) + Str("\"")
    num = Opt(Str("-")) + Rep(Range("09")) + Opt(Str(".") + Rep(Range("09")))
    name = (var | str_literal | num)

    start_pattern = ( Str("activate") + ws + var
                  + Opt(ws + Str("with") + ws + Str("(")
                    +   Str(*datatypes) + ws + var
                    +   Rep(Str(",") + ws + Str(*datatypes) + ws + var)
                    +   Str(")") )
                  + ws + Str("returns") + ws + Str(*datatypes) )

    end_pattern = Str("deactivate") + ws + var

    call_pattern = ( Str("warp(:") + Range("AZaz") + Rep(Range("AZaz09")) + Str(":)")
                 +   Opt(Str("(") + ws + name + Rep(ws + Str(",") + ws + name + ws) + Str(")")) )

    scanner.add_lexeme({
        "token": "functions_start",
        "pattern": start_pattern,
        "action": start_action
    })

    scanner.add_lexeme({
        "token": "functions_end",
        "pattern": end_pattern,
        "action": end_action
    })

    scanner.add_lexeme({
        "token": "functions_call",
        "pattern": call_pattern,
        "action": call_action
    })


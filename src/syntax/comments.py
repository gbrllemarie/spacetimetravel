
from plex import *

# define the action to execute when the token is detected
def action(scanner, text):
    scanner.write("/*" + text[2:-2] + "*/")

# add syntax to scanner
def apply(scanner):
    scanner.add_lexeme({
        "token": "comments",
        "pattern": Str("%%") + Rep(AnyBut("%%")) + Str("%%"),
        "action": action
    })

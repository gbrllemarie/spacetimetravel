
from plex import *

# define the action to execute when the token is detected
def action(scanner, text):
    scanner.write(text)

# add syntax to scnaner
def apply(scanner):
    scanner.add_lexeme({
        "token": "whitespace",
        "pattern": Any(" '\t\n"),
        "action": action
    })

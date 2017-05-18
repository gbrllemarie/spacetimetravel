
from modules.FileService import FileService
from plex import *

#implements the scanner for SpaceTime Travel
class SpaceTimeScanner:
    def __init__(self, file, name):
        self.source_file = file
        self.source_name = name
        self.lexicon = []
        self.actions = {}

        # initialize file service
        self.file_service = FileService(FileService.PRINT)

    # facilitates adding of new lexemes to the scanner's lexicon
    def add_lexeme(self, lexeme):
        self.actions[lexeme["token"]] = lexeme["action"]
        self.lexicon += [(lexeme["pattern"], lexeme["token"])]

    # facilitates adding of new states to the scanner's lexicon
    def add_state(self, state_name, sublexemes):
        lexemes = []

        for sublexeme in sublexemes:
            self.actions[sublexeme["token"]] = sublexeme["action"]
            lexemes += [(sublexeme["pattern"], sublexeme["token"])]

        self.lexicon.append( State(state_name, lexemes) )

    # wrapper for file service write
    def write(self, data):
        self.file_service.write(data)

    # wrapper for scanner state begin
    def begin(self, state):
        self.scanner.begin(state)

    # runs the scanner over the entire input file
    def start(self):
        # temporarily print out all unrecognized chars TODO: remove
        self.lexicon += [( AnyChar, IGNORE )]

        # initialize scanner
        self.scanner = Scanner(Lexicon(self.lexicon), self.source_file, self.source_name)

        # loop until EOF
        while 1:
            scanned = self.scanner.read()

            if scanned[0] is None:
                break

            # loop through each token in lexicon actions
            for token in self.actions:
                if scanned[0] == token:
                    # execute matched action
                    self.actions[token](self, scanned[1])

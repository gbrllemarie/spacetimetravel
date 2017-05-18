
class FileService:
    WRITE = True
    PRINT = False
    _OUTPUTMODE = PRINT

    # prepares output file if necessary; set global FileServiceMode
    # mode: boolean, you can also use FileService.WRITE or FileService.PRINT
    # filename: checked only on PRINT mode, must be a string with the name of the output file
    def __init__(self, mode, filename=None):
        if mode == self.PRINT:
            # print to stdout, we don't need to do anything
            pass
        elif mode == self.WRITE:
            # write to file
            self._OUTPUTMODE = self.WRITE;

            if filename == None:
                # no file specified
                raise SyntaxError("No filename passed to FileService init().");
            elif isinstance(filename, basestring):
                # output to file
                self._FILE = open(filename, "w")
            else:
                # filename isn't a string
                raise TypeError("Filename passed to FileService init() is not a string type.");
        else:
            # invalid mode
            raise TypeError("Inappropriate output mode passed to FileService init().")

    # facilitates output of generated syntax
    # data: string data to be outputted
    def write(self, data):
        if self._OUTPUTMODE == self.PRINT:
            print data,
        elif self._OUTPUTMODE == self.WRITE:
            self._FILE.write(data)
        else:
            raise AssertionError("Unable to determine FileService output mode.")



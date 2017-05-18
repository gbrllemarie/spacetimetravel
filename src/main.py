
import sys, os
import glob
from plex import *

from modules.SpaceTimeScanner import SpaceTimeScanner
import syntax

# validate argument count
if len(sys.argv) != 2:
    print("Invalid number of arguments.")
    exit()

# validate input file existence
if not os.path.isfile(sys.argv[1]):
    print("Unable to open input file.")
    sys.exit()

# read input source file
source_name = sys.argv[1]
source = open(source_name, "r")

# generate output file name
source_output = os.path.splitext(source_name)[0] + ".c"

# initialize scanner
scanner = SpaceTimeScanner(source, source_name)

# manually apply syntax modules in an approriate order
syntax.mainfn.apply(scanner)
syntax.functions.apply(scanner)
syntax.ifblock.apply(scanner)
syntax.forloop.apply(scanner)
syntax.variables.apply(scanner)
syntax.comments.apply(scanner)
syntax.whitespace.apply(scanner)

# begin scanning
scanner.start()

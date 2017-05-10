
import sys, os
from plex import *

# -- File Input Validation ----------------------------------------------------#
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

# -- Lexical Analysis ---------------------------------------------------------#

# generate the lexicon
lexicon = Lexicon([
	#-# reserved words #--------# actions #---------#
	  # data types
	( Str("numeral"),           "datatype_int"      ), # int datatype
	( Str("decimal"),           "datatype_float"    ), # float datatype
	( Str("star"),              "datatype_char"     ), # char datatype
	( Str("constellation"),     "datatype_string"   ), # string (char*) datatype
	( Str("day"),               "datatype_bool"     ), # bool datatype
	  # constants
	( Str("vacuum"),            "constant_void"     ), # void
	( Str("light"),             "constant_true"     ), # true
	( Str("darkness"),          "constant_false"    ), # false
	  # syntax
	( Str("loop"),              "syntax_for"        ), # for loop
	( Str("cycle"),             "syntax_while"      ), # while loop
	( Str("check"),             "syntax_if"         ), # if
	( Str("recheck"),           "syntax_elseif"     ), # else if
	( Str("retreat"),           "syntax_else"       ), # else
	  # helpers
	( Str("tick"),              "helper_increment"  ), # ++
	( Str("tock"),              "helper_decrement"  ), # --
	( Str("transform"),         "helper_typecast"   ), # type casting
	  # blocks
	( Str("ALPHA"),             "block_mainfnstart" ), # function start
	( Str("OMEGA"),             "block_mainfnend"   ), # function end
	( Str("activate"),          "block_fnstart"     ), # function start
	( Str("deactivate"),        "block_fnend"       ), # function end
	( Str("start"),             "block_start"       ), # block start
	( Str("end"),               "block_end"         ), # block end
	( Str("walangforever"),     "block_break"       ), # break
	( Str("magbbreakdinkayo"),  "block_continue"    ), # continue

	#-# names/identifiers #-----# actions #---------#
	  # TODO: Create lex entries for other syntax stuffs.
	  #       Consult the reference:
	  #       http://www.cosc.canterbury.ac.nz/greg.ewing/python/Plex/1.1.1/doc/Reference.html#AnyChar

	#-# other stuff #-----------# actions #---------#
	  # ...

	  # ignore all other unrecognized characters
	( AnyChar,                  IGNORE              ),
])

# -- Token Processing ---------------------------------------------------------#

# generate the scanner
scanner = Scanner(lexicon, source, source_output)

# read through the source input until EOF
while 1:
	token = scanner.read()
	print token
	if token[0] is None:
		break
	# TODO: this is where actions are defined for each token
	# this should contain each definition in the lexicon above,
	# specifying how it should convert itself to C code
	# (or convert the output into something that could be easily
	# converted into C).


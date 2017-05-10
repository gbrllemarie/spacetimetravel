
from plex import *

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
	# ...

	#-# other stuff #-----------# actions #---------#
	# ...

])

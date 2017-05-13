
import sys, os, re
from plex import *
from plex.traditional import re as rex
from StringIO import *

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

# general matching for tokens
ident_strip = Range("AZaz") + Rep(Range("AZaz09"))
identifier = Str(":") + ident_strip + Str(":")
integer = Rep1(Range("09")) 
number = integer + (Str(".")+Rep1(Range("09"))|Empty)
wspace = Rep(Str(" ")|Str("\t"))

# -- generate arrays for lexicon --------------------------#
# reserved words
lex_reserved = [
    #-# pattern #---------------# actions #---------#
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
    # ( Str("activate"),          "block_fnstart"     ), # function start
    # ( Str("deactivate"),        "block_fnend"       ), # function end
    ( Str("start"),             "block_start"       ), # block start
    ( Str("end"),               "block_end"         ), # block end
    ( Str("walangforever"),     "block_break"       ), # break
    ( Str("magbbreakdinkayo"),  "block_continue"    ) # continue
    #( Str("warp"),               Begin('helper_subprogram')   ), # sub program call
]

lex_datatypes = [
    # data types
    ( Str("numeral"),           "datatype_int"      ), # int datatype
    ( Str("decimal"),           "datatype_float"    ), # float datatype
    ( Str("star"),              "datatype_char"     ), # char datatype
    ( Str("constellation"),     "datatype_string"   ), # string (char*) datatype
    ( Str("day"),               "datatype_bool"     ) # bool datatype
]

lex_expr = [
    (Str("(")+Rep(AnyBut(""))+Str(")")+wspace,              "expr_paren"    ), # parenthesis
    # (Alt(identifier|number)+Rep(wspace+Any("+-")+wspace+Alt(identifier|number)),         "expr_addsub"    ), # addition and subtraction
    # (Alt(identifier|number)+Rep(wspace+Any("*/")+wspace+Alt(identifier|number)),         "expr_muldiv"    ), # multiplication and division
    (Alt(identifier|number)+Rep(wspace+Any("+-*/")+wspace+Alt(identifier|number)),         "expr_op"    ) # multiplication and division
]

fncall_token = Str("warp(") + identifier + Str(")(") + Rep(
    Opt(Alt(number,identifier)+Rep(Str(",")+Rep(wspace+(number|identifier)+wspace))
    ) +Str(")"))+Eol
lex_fncall = [
    ( fncall_token,           "helper_subprogram"    ), # add functional call to lexicon
]


comments_token = Str("%%") + Rep(AnyBut("%%")) + Str("%%")
lex_comments = [
    ( comments_token,           "syntax_comment"    ), # add comments to lexicon
]

vardec_token = Str("numeral", "decimal", "star", "day", "constellation") +wspace+ Str(":")+ ident_strip + Str(":")+Eol
lex_vardec = [
    ( vardec_token,           "syntax_vardec"    ), # add variable declaration to lexicon
]

# fns_token = Str("activate") + Rep(AnyBut("%%")) + Str("deactivate")
# lex_comments = [
#     ( fns_token,           "block_fnstart"    ), # add comments to lexicon
# ]

# TODO: Create lex entries for other syntax stuffs.
#       Consult the reference:
#       http://www.cosc.canterbury.ac.nz/greg.ewing/python/Plex/1.1.1/doc/Reference.html

# whitespaces and other formatting bits
lex_formatting = [
    ( Str(" "),                 "formatting_space"  ), # copy over spaces
    ( Str("\n"),                 "formatting_newline"  ), # copy over spaces
    ( Str("\t"),                "formatting_tab"    ), # copy over tabs
]

# other stuff
lex_misc = [
      # ignore all other unrecognized characters
    ( AnyChar, IGNORE),
]

lex_error = [
     ( AnyBut('\n'), "syn_error" ),
]

lex_tokens =  lex_reserved
lex_tokens += lex_expr
lex_tokens += lex_comments
lex_tokens += lex_vardec
lex_tokens += lex_formatting
# lex_tokens += lex_misc
lex_tokens += lex_fncall
lex_tokens += lex_error



# -- generate the lexicon ---------------------------------#
lexicon = Lexicon(lex_tokens)

# -- Token Processing ---------------------------------------------------------#

# generate the scanner
scanner = Scanner(lexicon, source, source_output)

def parseFns(token):
    fxn_name = token[1].split(' ')[1][1:-1]
    print token[1].split(' ')
    print token[1].split(' ')[1][1:-1]+"()"


def parseVardec(token):
    varname= token.split(':')[1]
    scan1 = Scanner(Lexicon(lex_datatypes), StringIO(token), source_output)
    tok = scan1.read()
    if tok[0] == "datatype_int":
        print "int "+str(varname)+";"
    elif tok[0] == "datatype_float":
        print "float "+str(varname)+";"
    elif tok[0] == "datatype_char":
        print "char "+str(varname)+";"
    elif tok[0] == "datatype_string":
        print "char* "+str(varname)+";"
    elif tok[0] == "datatype_bool":
        print "bool "+str(varname)+";"
    return

def parseFncall(token):
    tok = filter(None,re.split('\(|\)', str(token)))
    args = ""
    if(len(tok) > 2):
        raw_args = tok[2].split(',')
        for i in range(len(raw_args)):
            if raw_args[i][0] == ':' and raw_args[i][-1] == ':':
                raw_args[i] = raw_args[i][1:-1]
        args = ",".join(raw_args)
    print "/** function call to "+tok[1][1:-1]+" **/"
    print tok[1][1:-1]+"("+args+");"
    return

# def parseExprOp(token, op):
#     tok = filter(None,re.split(op, str(token)))
#     if(len(tok) > 1):
#         for i in range(len(tok)):
#             print str(parseExprOp(tok[0],'\/'))+" * "
#     else:
#         return tok

# read through the source input until EOF
linenum = 0
while 1:
    linenum += 1
    token = scanner.read()
    
    # print token
    if token[0] is None:
        break
    # TODO: this is where actions are defined for each token
    # this should contain each definition in the lexicon above,
    # specifying how it should convert itself to C code
    # (or convert the output into something that could be easily
    # converted into C).

    # -- data types
    elif token[0] == "datatype_int":
        print "int"
    elif token[0] == "datatype_float":
        print "float"
    elif token[0] == "datatype_char":
        print "char"
    elif token[0] == "datatype_string":
        print "char*"
    elif token[0] == "datatype_bool":
        print "bool"
        

    # -- constants   
    elif token[0] == "constant_void":
        print "void"
        
    elif token[0] == "constant_true":
        print "true"
        
    elif token[0] == "constant_false":
        print "false"
        

    # -- syntax
    elif token[0] == "syntax_for":
        print "for"
    elif token[0] == "syntax_while":
        print "while"
    elif token[0] == "syntax_if":
        print "if"
    elif token[0] == "syntax_elseif":
        print "else if"
    elif token[0] == "syntax_else":
        print "else"
    elif token[0] == "syntax_comment":
        print "/*" + token[1][2:-2] + "*/"
        print token
    elif token[0] == 'syntax_vardec':
        parseVardec(token[1])

    # -- helpers
    elif token[0] == "helper_increment":
        print "++"
    elif token[0] == "helper_decrement":
        print "--"
    elif token[0] == "helper_typecast":
        print "(typecast here)"                        # TODO
    elif token[0] == "helper_subprogram":
        parseFncall(token[1])

    # -- blocks
    elif token[0] == "block_mainfnstart":
        print "int main() {\n"
        fileout.write("int main() {\n")
    elif token[0] == "block_mainfnend":
        print "return 0;\n}\n"
        fileout.write("return 0;\n}\n")
    elif token[0] == "block_fnstart":
        print "fxn_name() {\n"
        # parseFns(token)

    elif token[0] == "block_fnend":
        print "}\n"
        fileout.write("}\n")
    elif token[0] == "block_start":
        print "{\n"
        fileout.write("{\n")
    elif token[0] == "block_end":
        print "}\n"
        fileout.write("}\n")
    elif token[0] == "block_break":
        print "break;"
        fileout.write("break;\n")
    elif token[0] == "block_continue":
        print "continue;"
        fileout.write("continue;\n")

    # -- others
    elif token[0] == "formatting_space":
        print " ",
    elif token[0] == "formatting_tab":
        print "\t",
    elif token[0] == "formatting_newline":
        linenum -= 1
        pass
    elif token[0] == "expr_paren":
        print token
    elif token[0] == "expr_addsub":
        print token
    elif token[0] == "expr_muldiv":
        print token
    # elif token[0] == "expr_op":
    #     parseExprOp(token[1], '\*')

    # Insert more todos here
    else:
        print token
        print "syntax error on line "+str(linenum)
        break

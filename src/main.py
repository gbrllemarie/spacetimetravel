
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
wspace      = Rep(Any(" \t"))
ident_strip = Range("AZaz") + Rep(Range("AZaz09"))
identifier  = wspace + Str(":") + ident_strip + Str(":") + wspace
integer     = Rep1(Range("09"))
number      = integer + (Str(".") + Rep1(Range("09")) | Empty)
dtype       = Str("numeral")|Str("decimal")|Str("star")|Str("constellation")|Str("day")|Str("vacuum")


# -- generate arrays for lexicon --------------------------#
# reserved words
lex_expr_paren_newline = Str("(")+Rep(AnyBut("\n"))+Str(")")+wspace
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
    ( Str("receive") + identifier,           "syntax_scanf"       ), # scanf
    ( Str("display") + identifier,           "syntax_printf"       ), # printf
      # helpers
    ( Str("tick") + lex_expr_paren_newline,              "helper_increment"  ), # ++
    ( Str("tock") + lex_expr_paren_newline,              "helper_decrement"  ), # --
    ( Str("transform"),         "helper_typecast"   ), # type casting
      # blocks
    # ( Str("ALPHA"),             "block_mainfnstart" ), # function start
    # ( Str("OMEGA"),             "block_mainfnend"   ), # function end
    # ( Str("activate"),          "block_fnstart"     ), # function start
    # ( Str("deactivate"),        "block_fnend"       ), # function end
    ( Str("start"),             "block_start"       ), # block start
    ( Str("end"),               "block_end"         ), # block end
    ( Str("walangforever"),     "block_break"       ), # break
    ( Str("magbbreakdinkayo"),  "block_continue"    ) # continue
    #( Str("warp"),               Begin('helper_subprogram')   ), # sub program call
]

# global dictionary that stores variables and their types
# keys are the variables and values are their types
# { "x": "int", "str": "char *" }
variable_types_dict = {}

# datatypes and parsing
lex_datatypes = [
    # data types
    ( Str("numeral"),           "datatype_int"      ), # int datatype
    ( Str("decimal"),           "datatype_float"    ), # float datatype
    ( Str("star"),              "datatype_char"     ), # char datatype
    ( Str("constellation"),     "datatype_string"   ), # string (char[n]) datatype
    ( Str("day"),               "datatype_bool"     ), # bool datatype
]

vardec_token = ( Str("numeral", "decimal", "star", "day", "constellation")
               + wspace + identifier +Opt(Str("<")+integer+Str(">"))+ Eol )
lex_vars = [
    ( vardec_token,             "syntax_vardec"     ), # variable declaration
    ( identifier + Str("<-"),   "syntax_varassign"  ), # variable assignment
]

# main function
mainfn_start_token = Str("ALPHA") + wspace + Str(":time:") + wspace
mainfn_end_token   = Str("OMEGA") + wspace + Str(":time:") + wspace
lex_mainfn = [
    ( mainfn_start_token,       "block_mainfnstart" ),
    ( mainfn_end_token,         "block_mainfnend"   ),
]

# functions
fncall_token = (Str("warp(")
              + identifier
              + Str(")(")
              + Opt(Alt(number, identifier)
                      + Rep(Str(",") + Rep(wspace + (number|identifier) + wspace)
                      )
               )+Str(")")+Eol)
fnhead_token = Str("activate")+identifier+Str("with ")+Str("(")+ wspace+Rep(Opt(dtype+Alt(number, identifier)
            + Rep(Str(",") + Rep(wspace+dtype+wspace + (number|identifier) + wspace)
            ))
            )+ Str(")") + wspace + Opt(Str("returns")+wspace+dtype)
lex_fncall = [
    ( fncall_token,                         "helper_subprogram" ), # add functional calls
    ( Str("transmit")+wspace+Alt(identifier|number),"helper_return" ), # add function return
    ( fnhead_token,                         "helper_fnheader" ), # add function header
    ( Str("deactivate")+wspace+identifier,  "helper_fnfooter" ), # add function header
]

# expressions
lex_expr_paren = Str("(")+Rep(AnyBut(""))+Str(")")+wspace
lex_expr_op = Alt(identifier|number)+Rep(wspace+Any("+-*/")+wspace+Alt(identifier|number))
lex_expr = [
    ( lex_expr_paren,           "expr_paren"        ), # parenthesis
    # (Alt(identifier|number)+Rep(wspace+Any("+-")+wspace+Alt(identifier|number)),         "expr_addsub"    ), # addition and subtraction
    # (Alt(identifier|number)+Rep(wspace+Any("*/")+wspace+Alt(identifier|number)),         "expr_muldiv"    ), # multiplication and division
    ( lex_expr_op,              "expr_op"           ) # multiplication and division
]

# comments
comments_token = Str("%%") + Rep(AnyBut("%%")) + Str("%%")
lex_comments = [
    ( comments_token,           "syntax_comment"    ), # add comments to lexicon
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
    ( Str("\n"),                "formatting_newline"), # copy over newlines
    ( Str("\t"),                "formatting_tab"    ), # copy over tabs
]

# other stuff
lex_misc = [
      # ignore all other unrecognized characters
    ( AnyChar, IGNORE),
]


lex_error = [
     ( AnyBut("\n"), "syntax_error" ),
]

# main function
#mainfn_start_token = Str("ALPHA") + wspace + Str(":time:") + wspace
#mainfn_end_token   = Str("OMEGA") + wspace + Str(":time:") + wspace
#lex_mainfn = [
#    ( mainfn_start_token,       "block_mainfnstart" ),
#    ( mainfn_end_token,         "block_mainfnend"   ),
#]

#for_condition = Str ("(since") + EXPRESSION + wspace + Str("until") + EXPRESSION + wspace +Str("do") TICK OR TOCK + Str(")")
#lex_for = [
#    ( Str("start loop"), "syntax_for"),
#    ( Str("end loop"), "syntax_for_end"),
#    ( for_condition, "syntax_for_condition"),
#]

#while_condition = Str ("(until") + EXPRESSION + Str(")")
#lex_while = [
#    ( Str("start cycle"), "syntax_while"),
#    ( Str("end cycle"), "syntax_while_end"),
#    ( while_condition, "syntax_while_condition"),
#]

# -- generate the lexicon ---------------------------------#
# put everything together
lex_tokens =  lex_reserved
lex_tokens += lex_mainfn
lex_tokens += lex_expr
lex_tokens += lex_comments
lex_tokens += lex_vars
lex_tokens += lex_formatting
# lex_tokens += lex_misc
lex_tokens += lex_fncall
lex_tokens += lex_error

lexicon = Lexicon(lex_tokens)

# -- Token Processing ---------------------------------------------------------#

# generate the scanner
scanner = Scanner(lexicon, source, source_output)


def getName(str1):
    return str1.replace(':', '')

def getDtype(type):
    list_type =  {'numeral':'int', 'decimal': 'float', 'star':'char', 'constellation': 'char *','day':'bool'}
    return list_type[type]

def parseFns(token):
    fxn_name = token[1].split(" ")[1][1:-1]
    print token[1].split(" ")
    print token[1].split(" ")[1][1:-1]+"()"

def parseVardec(token):
    varname = token.split(':')[1]
    scan1 = Scanner(Lexicon(lex_datatypes), StringIO(token), source_output)
    tok = scan1.read()
    if tok[0] == "datatype_int":
        print "int "+str(varname),
        setDictVarAndType(varname, "int")
    elif tok[0] == "datatype_float":
        print "float "+str(varname),
        setDictVarAndType(varname, "float")
    elif tok[0] == "datatype_char":
        print "char "+str(varname),
        setDictVarAndType(varname, "char")
    elif tok[0] == "datatype_string":
        print "char  "+str(varname),
        setDictVarAndType(varname, "char-array")
    elif tok[0] == "datatype_bool":
        print "bool "+str(varname),
        setDictVarAndType(varname, "bool")

    temp = filter(None,token.split(':'))
    if(len(temp) > 2):
        print "["+temp[2][1:-1]+"]",
    print ";",
    return

def setDictVarAndType(var, type):
    variable_types_dict[var] = type

def typeof(variable):
    variable_type = variable_types_dict[variable]
    return variable_type

def parseScanInput(token):
    varname = token.split(':')[1].strip()
    format_code = ""

    # print "varname: ", varname
    # print "typeof(varname): ", typeof(varname)
    
    if typeof(varname) == "int":
        format_code = "%d"
        varname = "&" + varname
    elif typeof(varname) == "float":
        format_code = "%lf"
        varname = "&" + varname
    elif typeof(varname) == "char": 
        format_code = "%c"
        varname = "&" + varname
    elif typeof(varname) == "char-array": 
        format_code = "%s"

    scanf = 'scanf("'
    c_scan_string = scanf + format_code + '", ' + varname + ");"
    
    return c_scan_string

def parsePrintInput(token): 
    varname = token.split(':')[1].strip()
    format_code = ""

    if typeof(varname) == "int":
        format_code = "%d"
    elif typeof(varname) == "float":
        format_code = "%.2f"
    elif typeof(varname) == "char": 
        format_code = "%c"
    elif typeof(varname) == "char-array": 
        format_code = "%s"

    printf = '"printf("'
    c_print_string = printf + format_code + '", ' + varname + ");"
    
    return c_print_string

def increment_or_decrement(token, incr_decr_concat):
    varname = token.split(':')[1].strip()

    if incr_decr_concat == "++" or incr_decr_concat == "--":
        varname = varname + incr_decr_concat + ";"
    else:
        return "Error occured with helper"
    return varname

def parseFnheader(token):
    # 0 - activate, 1 - fname, 2 - with, 3 - args, -2- returns, -1 - return type
    tok = token.split(' ')
    fname = getName(tok[1])
    args = (' '.join(tok[3:-2])).strip('()')
    args = filter(None,args.split(','))
    return_type = tok[-1]

    print getDtype(return_type)+" "+fname+" (",
    for i in range(len(args)):
        if i > 0:
            print ", ",
        temp = filter(None,args[i].split(' '))
        print getDtype(temp[0])+" "+getName(temp[1]),
    print ") {",


def parseFncall(token):
    tok = filter(None,re.split('\(|\)', str(token)))
    args = ""
    if(len(tok) > 2):
        raw_args = tok[2].split(',')
        for i in range(len(raw_args)):
            if raw_args[i][0] == ':' and raw_args[i][-1] == ':':
                raw_args[i] = raw_args[i][1:-1]
        args = ",".join(raw_args)
    print tok[1][1:-1]+"("+args+");",
    print "/** function call to "+tok[1][1:-1]+" **/"
    return


def parseFnreturn(token):
    tok = token.split(' ')
    tok[1] = tok[1].replace(':', '')
    print "return "+tok[1]+";"

def parseExprOp(token, end=1):
    token = token.replace(":","")
    if end == 1:
        token = token+";"
    return token

def parseExprParen(token):
    strip_token = token[1:-1] #remove enclosing parentheses
    scan1 = Scanner(Lexicon(lex_expr), StringIO(strip_token), source_output)
    tok = scan1.read()
    #if tok[0] == ""
    

# read through the source input until EOF
linenum = 1
while 1:
    token = scanner.read()
    # print token
    linenum += token[1].count("\n")
    # print linenum
    if token[0] is None:
        break
    # TODO: this is where actions are defined for each token
    # this should contain each definition in the lexicon above,
    # specifying how it should convert itself to C code
    # (or convert the output into something that could be easily
    # converted into C).

    # -- data types
    elif token[0] == "datatype_int":
        print "int",
    elif token[0] == "datatype_float":
        print "float",
    elif token[0] == "datatype_char":
        print "char",
    elif token[0] == "datatype_string":
        print "char*",
    elif token[0] == "datatype_bool":
        print "bool",

    # -- constants   
    elif token[0] == "constant_void":
        print "void",
    elif token[0] == "constant_true":
        print "true",
    elif token[0] == "constant_false":
        print "false",

    # -- syntax
    elif token[0] == "syntax_for":
        print "for",
    elif token[0] == "syntax_while":
        print "while",
    elif token[0] == "syntax_if":
        print "if",
    elif token[0] == "syntax_elseif":
        print "else if",
    elif token[0] == "syntax_else":
        print "else",
    elif token[0] == "syntax_comment":
        print "/*" + token[1][2:-2] + "*/",
    elif token[0] == "syntax_vardec":
        parseVardec(token[1])
    elif token[0] == 'syntax_scanf': 
        print parseScanInput(token[1])
    elif token[0] == 'syntax_printf': 
        print parsePrintInput(token[1])
    elif token[0] == 'syntax_varassign':
        tok = token[1].replace(":","")
        tok = tok.replace("<-"," =")
        print tok,

    # -- helpers
    elif token[0] == "helper_increment":
        c_output = increment_or_decrement(token[1], "++")
        print c_output
    elif token[0] == "helper_decrement":
        c_output = increment_or_decrement(token[1], "--")
        print c_output
    elif token[0] == "helper_typecast":
        print "(typecast here)",                       # TODO
    elif token[0] == "helper_subprogram":
        parseFncall(token[1])
    elif token[0] == "helper_return":
        parseFnreturn(token[1])
    elif token[0] == "helper_fnheader":
        parseFnheader(token[1])
    elif token[0] == "helper_fnfooter":
        print "}"

    # -- blocks
    elif token[0] == "block_main":
        print "main",

    elif token[0] == "block_mainfnstart":
        print "int main() {",
        #fileout.write("int main() {\n")
    elif token[0] == "block_mainfnend":
        print "return 0;\n}",
        #fileout.write("return 0;\n}\n")
    elif token[0] == "block_fnstart":
        #print "fxn_name() {",
        pass

    elif token[0] == "block_fnend":
        print "}",
        #fileout.write("}\n")
    elif token[0] == "block_start":
        print "{",
        #fileout.write("{\n")
    elif token[0] == "block_end":
        print "}",
        #fileout.write("}\n")
    elif token[0] == "block_break":
        print "break;",
        #fileout.write("break;\n")
    elif token[0] == "block_continue":
        print "continue;",
        #fileout.write("continue;\n")

    # -- others
    elif token[0] == "formatting_space":
        print " ",
    elif token[0] == "formatting_tab":
        print "\t",
    elif token[0] == "formatting_newline":
        print "\n",
    elif token[0] == "expr_paren":
        print token,
    elif token[0] == "expr_addsub":
        print token,
    elif token[0] == "expr_muldiv":
        print token,
    elif token[0] == "expr_op":
        print parseExprOp(token[1])

    # Insert more todos here
    else:
        print token
        print "syntax error on line "+str(linenum)
        break


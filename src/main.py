
import sys, os, re
from plex import *
from plex.traditional import re as rex
import re as regex
from StringIO import *


import ply_test.ply_parse as ply

status = ply.startParse()

if status != True:
    exit()

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
quote       = '\"'
wspace      = Rep(Any(" \t"))
ident_strip = Range("AZaz") + Rep(Range("AZaz09"))
identifier  = wspace + Str(":") + ident_strip + Str(":") + wspace
integer     = Rep1(Range("09"))
number      = integer + (Str(".") + Rep1(Range("09")) | Empty)
dtype       = Str("numeral")|Str("decimal")|Str("starz")|Str("constellation")|Str("day")|Str("vacuum")
equality_operators = Str("?>") | Str("?<") | Str("?>=") | Str("?<=") | Str("?=") | Str("?!=")
anyString = wspace +Str("\"") + Rep(AnyBut(quote)) + Str("\"") + wspace
array_index = Opt(Str("<")+(integer|identifier)+Str(">"))
# check_token = wspace + Str("(")+ Rep(Range("AZaz09")) + wspace + equality_operators + wspace + Rep(Range("AZaz09")) + Str(")")

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
    # ( Str("loop"),              "syntax_for"        ), # for loop
    # ( Str("cycle"),             "syntax_while"      ), # while loop
    ( Str("start check")+wspace+lex_expr_paren_newline,       "syntax_if"         ), # if
    ( Str("recheck")+wspace+lex_expr_paren_newline,           "syntax_elseif"     ), # else if
    ( Str("retreat"),           "syntax_else"       ), # else
    ( Str("receive") + identifier + array_index,           "syntax_scanf"       ), # scanf
    ( (Str("display")|Str("displayln")) + identifier 
    +  array_index,           "syntax_printf"       ), # printf
    ( (Str("display")|Str("displayln")) + anyString,           "syntax_for_print"),    # equivalent printf("string");
      # helpers
    ( Str("tick") + lex_expr_paren_newline,              "helper_increment"  ), # ++
    ( Str("tock") + lex_expr_paren_newline,              "helper_decrement"  ), # --
    ( Str("transform"),         "helper_typecast"   ), # type casting
      # blocks
    # ( Str("ALPHA"),             "block_mainfnstart" ), # function start
    # ( Str("OMEGA"),             "block_mainfnend"   ), # function end
    # ( Str("activate"),          "block_fnstart"     ), # function start
    # ( Str("deactivate"),        "block_fnend"       ), # function end
    # ( Str("start check"),       "block_start_if"       ), # block start
    ( Str("end check"),         "block_end_if"         ), # block end check
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
    ( Str("starz"),              "datatype_char"     ), # char datatype
    ( Str("constellation"),     "datatype_string"   ), # string (char[n]) datatype
    ( Str("day"),               "datatype_bool"     ), # bool datatype
]

array_element = wspace + identifier + (Str("<")+(integer|identifier)+Str(">")) + wspace
vardec_token = ( Str("numeral", "decimal", "starz", "day", "constellation")
               + wspace + identifier +Opt(Str("<")+integer+Str(">"))+ Eol )
lex_vars = [
    ( vardec_token,             "syntax_vardec"     ), # variable declaration
    ( identifier +Opt(Str("<")+(integer|identifier)+Str(">"))+wspace+ Str("<-"),   "syntax_varassign"  ), # variable assignment
    ( identifier +wspace+ Str("<-") + anyString, "syntax_varassign_string"),
    ( identifier +wspace + Str("<-") + array_element, "syntax_varassign_array"),
    ( array_element +wspace + Str("<-") + array_element, "syntax_varassign_array2"),
    #( identifier + Str("<-") + (Str("light")|Str("darkness")))
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
              + Rep(AnyBut("\n"))+Str(")")+Eol)
fnhead_token = Str("activate")+identifier+Str("with (")+ wspace+Opt(dtype+Alt(number, identifier)
            + Rep(Str(",") + wspace+dtype+wspace + (number|identifier) + wspace)
            ) + Str(")") + wspace + Opt(Str("returns")+wspace+dtype)
lex_fncall = [
    ( fncall_token,                         "helper_subprogram" ), # add functional calls
    ( Str("transmit")+wspace+Alt(identifier+array_index|number),"helper_return" ), # add function return
    ( fnhead_token,                         "helper_fnheader" ), # add function header
    ( Str("deactivate")+wspace+identifier,  "helper_fnfooter" ), # add function header
]

# expressions
lex_expr_paren = Str("(")+Rep(AnyBut("\n"))+Str(")")+wspace
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

for_condition = Str ("since ") + Rep(AnyBut("\n")) + Str(" until ") + Rep(AnyBut("\n")) +Str(" do ") + Rep(AnyBut("\n"))|(Str("tick(")|Str("tock(")+identifier+Str(")")) + Str(")\n")
lex_for = [
   ( Str("start loop"), "syntax_for"),
   ( Str("end loop"), "syntax_for_end"),
   ( for_condition, "syntax_for_condition"),
]

while_condition = Str ("(until ") + Rep(AnyBut("\n")) + Str(")\n")
lex_while = [
   ( Str("start cycle"), "syntax_while"),
   ( Str("end cycle"), "syntax_while_end"),
   ( while_condition, "syntax_while_condition"),
]

# -- generate the lexicon ---------------------------------#
# put everything together
lex_tokens =  lex_reserved
lex_tokens += lex_mainfn
lex_tokens += lex_expr
lex_tokens += lex_comments
lex_tokens += lex_vars
lex_tokens += lex_formatting
lex_tokens += lex_for
lex_tokens += lex_while
# lex_tokens += lex_misc
lex_tokens += lex_fncall
lex_tokens += lex_error

lex_paren = lex_for
lex_paren += [(lex_expr_op,"expr_op")]


lexicon = Lexicon(lex_tokens)

# -- Token Processing ---------------------------------------------------------#

# generate the scanner
scanner = Scanner(lexicon, source, source_output)

def getName(str1):
    return str1.replace(':', '')

def getDtype(type):
    list_type =  {'numeral':'int', 'decimal': 'float', 'star':'char', 'constellation': 'char *','day':'bool','vacuum':'void'}
    return list_type[type]

def translateFns(token):
    fxn_name = token[1].split(" ")[1][1:-1]
    print token[1].split(" ")
    print token[1].split(" ")[1][1:-1]+"()"

def addVarDataType(var):
    varname = var.split(':')[1]
    scan1 = Scanner(Lexicon(lex_datatypes), StringIO(var), source_output)
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

def translateVardec(token):
    varname = token.split(':')[1]
    addVarDataType(token)

    temp = filter(None,token.strip(' ').split(':'))
    if(len(temp) > 2):
        print "["+temp[2].strip('<>')+"]",
    print ";",
    return

def setDictVarAndType(var, type):
    variable_types_dict[var] = type

def typeof(variable):
    variable_type = variable_types_dict[variable]
    return variable_type

def translateScanInput(token):
    varname = token.split(':')[1].strip()
    format_code = ""
    var_index = ""
    # print "varname: ", varname
    # print "typeof(varname): ", typeof(varname)
    
    if typeof(varname) == "int":
        format_code = "%d"
        varname = "&" + varname
    elif typeof(varname) == "float":
        format_code = "%f"
        varname = "&" + varname
    elif typeof(varname) == "char": 
        format_code = "%c"
        varname = "&" + varname
    elif typeof(varname) == "char-array": 
        format_code = "%s"

    if len(filter(None,token.split(':'))) > 2:
        var_index = ''.join(token.split(':')[2:]).strip('<>')
        var_index = "["+var_index+"]"
        varname = varname+ var_index

    scanf = 'scanf("'
    c_scan_string = scanf + format_code + '", ' + varname + ");"
    
    return c_scan_string

def translateAssignVar2(token):
    tok = token.replace(":","")
    tok = tok.replace("<-"," =")
    tok = tok.replace("<", "[")
    tok = tok.replace(">", "]")
    return tok + ";"

def translateAssignVar(token):
    tok = token.replace(":","")
    tok = tok.replace("<-"," =")
    tok = tok.replace("<", "[")
    tok = tok.replace(">", "]")
    return tok
# translates
# str<- "hello" to trcopy
def translateAssignString(token):
    tok_split = token.split(':')
    tok_new = token.split('"')
    varname = tok_split[1].strip()
    if typeof(varname) == "char-array":
        tok = ""
        tok = "strcpy(" + varname + ",\"" + tok_new[1] + "\");"
        return tok
    else:
        print "Error :%s: is not a string in line %d" % (varname,linenum)
        exit()

def translatePrintString(token):
    first_tok = token.split(' ')
    tok_split = token.split('\"')
    tok = tok_split[1]
    printTok = "printf(\"" + tok
    newline = r"\n"
    if (first_tok[0] == 'display'):
        printTok = "printf(\"" + tok + "\");"
    else:
        printTok = "printf(\"" + tok + newline + "\");"
    return printTok

def translatePrintInput(token):
    tok_split = filter(None,token.split(':'))
    varname = tok_split[1].strip()
    format_code = ""
    newline = ""
    var_index = ""
    if len(tok_split) > 2:
        var_index = ''.join(tok_split[2:]).strip('<>')
        var_index = "["+var_index+"]"
    if(tok_split[0].strip(' ') == 'displayln'):
        newline = "\\n"
    try:    
        if typeof(varname) == "int":
            format_code = "%d"
        elif typeof(varname) == "float":
            format_code = "%.2f"
        elif typeof(varname) == "char": 
            format_code = "%c"
        elif typeof(varname) == "char-array": 
            format_code = "%s"

        printf = 'printf("'
        c_print_string = printf + format_code + ' '+newline+'",' + varname +var_index+ ");"
        
        return c_print_string
    except:
        print "\nERROR: Variable "+varname+" has no datatype or has not been declared"
        exit()

def increment_or_decrement(token, incr_decr_concat):
    varname = token.split(':')[1].strip()

    if incr_decr_concat == "++" or incr_decr_concat == "--":
        varname = varname + incr_decr_concat + ";"
    else:
        return "Error occured with helper"
    return varname

def translateFnheader(token):
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
        addVarDataType(args[i].strip(' '))
        # temp = filter(None,args[i].split(' '))
        # print getDtype(temp[0])+" "+getName(temp[1]),
    print ") {",


def translateFncall(token):
    tok = filter(None,re.split('\(|\)', str(token)))
    args = ""
    if(len(tok) > 2):
        raw_args = tok[2].split(',')
        for i in range(len(raw_args)):
            raw_args[i] = raw_args[i].strip(' ')
            raw_args[i] = raw_args[i].replace(':', '')
        args = ",".join(raw_args)
    print tok[1][1:-1]+"("+args+");",
    print "/** function call to "+tok[1][1:-1]+" **/"
    return


def translateFnreturn(token):
    tok = token.split(' ')
    tok[1] = tok[1].replace(':', '')
    tok[1] = tok[1].replace('<', '[')
    tok[1] = tok[1].replace('>', ']')
    print "return "+tok[1]+";"

def translateExprOp(token, end=1):
    token = token.replace(":","")
    if end == 1:
        token = token+";"
    return token

def translateExprParen(token):
    strip_token = token[1:-1] #remove enclosing parentheses
    scan1 = Scanner(Lexicon(lex_paren), StringIO(strip_token), source_output)
    tok = scan1.read()
    # print tok
    trans = "("
    if tok[0] == 'syntax_for_condition':
        trans += translateForLoop(tok[1])
    else:
        temp = tok[1]
    return trans

def translateVarAssign(token):
    temp = token.replace("?=", "==")
    temp = temp.replace("?|","||")
    temp = temp.replace("?&","&&")
    temp = temp.replace("mod","%")
    temp = temp.replace("?","")
    temp = temp.replace(":","")
    temp = temp.replace("<-","=")
    return temp


def translateIfElseIfElseClause(spacetime_syntax, c_syntax, token):
    c_if_syntax = token.replace(spacetime_syntax, c_syntax)
    c_if_syntax = translateVarAssign(c_if_syntax)
    c_if_syntax = c_if_syntax + "{"
    #c_if_syntax = c_if_syntax.replace("<", "[")
    #c_if_syntax = c_if_syntax.replace(">", "]")
    tok_split = c_if_syntax.split(' ')
    curr = 0
    for x in tok_split:
        #print "len!!"
        #print len(x)
        if len(x) > 2:
            tok_split[curr] = tok_split[curr].replace("<","[")
            tok_split[curr] = tok_split[curr].replace(">", "]")
        curr = curr + 1

    token_fin = ""
    for x in tok_split:
        token_fin += x + " "
    #print "ANNYEONG LOOOK HRE"
    #print token_fin
    #print " ANNYEONG"
    return token_fin

def translateForLoop(token):
    trans = ""
    temp = token.replace("since", "")
    temp = temp.replace(" until", ";")
    temp = temp.replace(" do", ";")
    temp1 = temp.split(";")
    for i in temp1:
        trans += translateVarAssign(i) + "; "
    trans = trans.strip("; ")
    trans += ") {"
    return trans

def translateWhileLoop(token):
    cond = token.replace('until', '')
    cond = translateVarAssign(cond)
    cond += "{"
    return cond




# def trans

# read through the source input until EOF
linenum = 1
preprocess = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <stdbool.h>\n"
preprocess += "\n#define darkness false \n#define light true"
preprocess += "\n#define tick(x) x++ \n#define tock(x) x--"
print preprocess
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
        print "void;",
    elif token[0] == "constant_true":
        print "true;",
    elif token[0] == "constant_false":
        print "false;",

    # -- syntax
    elif token[0] == "syntax_for":
        print "for",
    elif token[0] == "syntax_for_condition":
        print translateForLoop(token[1])
    elif token[0] == "syntax_for_end":
        print "}"
    elif token[0] == "syntax_while":
        print "while",
    elif token[0] == "syntax_while_end":
        print "}",
    elif token[0] == "syntax_while_condition":
        print translateWhileLoop(token[1])

    elif token[0] == "syntax_if":
        print translateIfElseIfElseClause("start check", "if", token[1])
    elif token[0] == "syntax_elseif":
        print translateIfElseIfElseClause("recheck", "}\nelse if", token[1])
    elif token[0] == "syntax_else":
        print translateIfElseIfElseClause("retreat", "}\nelse", token[1])
    elif token[0] == "block_end_if":
        print "}"
    elif token[0] == "syntax_comment":
        print "/*" + token[1][2:-2] + "*/",
    elif token[0] == "syntax_vardec":
        translateVardec(token[1])
    elif token[0] == 'syntax_scanf': 
        print translateScanInput(token[1])
    elif token[0] == 'syntax_for_print': 
        print translatePrintString(token[1])
    elif token[0] == 'syntax_printf': 
        print translatePrintInput(token[1])
    elif token[0] == 'syntax_varassign_string':
        print translateAssignString(token[1])
    elif token[0] == 'syntax_varassign':
        print translateAssignVar(token[1])
    elif token[0] == 'syntax_varassign_array':
        print translateAssignVar2(token[1])
    elif token[0] == 'syntax_varassign_array2':
        print translateAssignVar2(token[1])
    
        #tok = token[1].replace(":","")
        #tok = tok.replace("<-"," =")
        #print tok,

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
        translateFncall(token[1])
    elif token[0] == "helper_return":
        translateFnreturn(token[1])
    elif token[0] == "helper_fnheader":
        translateFnheader(token[1])
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
    elif token[0] == "block_start_if":
        print "{",
        #fileout.write("{\n")
    elif token[0] == "block_end_if":
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
        print translateExprParen(token[1])
    elif token[0] == "expr_addsub":
        print token,
    elif token[0] == "expr_muldiv":
        print token,
    elif token[0] == "expr_op":
        print translateExprOp(token[1])

    # Insert more todos here
    else:
        print token
        print "syntax error on line "+str(linenum)
        break
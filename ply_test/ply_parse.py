import ply.lex as lexy
import sys
import ply.yacc as yacc
########## LIST OF STATES ########################
# states = (
#    ('foo','exclusive'),
#    ('bar','inclusive'),
# )

########## LIST OF TOKENS #########################
tokens = ('COMMENTS',  )

############ REGEX FOR TOKENS ######################
wspace      = r"[ \t]*"
ident_strip = r"([A-Za-z][A-Za-z0-9]*)"
identifier 	= r"("+wspace+':'+ident_strip+':'+wspace+")"
t_identifier  = r''+wspace+identifier+wspace
integer     = r'[0-9]+'
t_intnum	= integer
t_floatnum    = r'('+integer+'\.'+integer+')'
t_dtype       = r"numeral|decimal|constellation|day|vacuum" 
# temporarily removed ``star'' since it conflicts with start cycle/loop

tok_atoms = ('ident_strip','identifier', 'intnum', 'floatnum', 'dtype',)

##### TOKENS FOR SYMBOLS ####
t_LPAREN  		= r'\('
t_RPAREN  		= r'\)'
t_OPERATION 	= r'(\+|-|\*|\/)'
t_RELATIONAL 	= r"\?(!?=|>=?|<=?)"
t_RELATIONALBIT = r"(\&\&|\|\|)"
t_MOD			= r"(mod)"
t_COMMA			= r','
# t_PLUS    = r'\+'
# t_MINUS   = r'-'
# t_TIMES   = r'\*'
# t_DIVIDE  = r'/'
t_ASSIGN  = r"<-"

tok_symbols = ('OPERATION', 'ASSIGN', 'LPAREN','RPAREN',
	'RELATIONAL', 'RELATIONALBIT', 'MOD', 'COMMA')

##### TOKENS FOR FUNCTIONS ######

t_INITIAL_main_head = r"(ALPHA"+wspace+":time:)"
t_INITIAL_main_foot = r"(OMEGA"+wspace+":time:)"

tok_mainfxn = ('main_head', 'main_foot',)

t_INITIAL_fxn_head = r"activate"+identifier
t_INITIAL_fxn_foot = r"deactivate"+identifier
t_FXNRETURN = r"(returns)"
t_FXNWITH = r"(with)"


t_fxn_return = r"(transmit"+wspace+")"

tok_fxn =  ('fxn_head', 'fxn_foot', 'fxn_return', 'FXNRETURN', 'FXNWITH')

####### TOKENS FOR STATEMENTS #################
## TOKEN FOR LOOPS ##


t_START_CYCLE	= r"(start\ cycle)"
t_END_CYCLE		= r"(end\ cycle)"
t_START_LOOP	= r"(start\ loop)"
t_END_LOOP		= r"(end\ loop)"
t_UNTIL			= r"(until)"
t_SINCE			= r"(since)"
t_DO 			= r"(do)"
t_TICKTOK		= r"(tick|tock)\("

tok_loops = ('START_CYCLE', 'END_CYCLE',
	'START_LOOP', 'END_LOOP', 'UNTIL', 'SINCE', 'DO', 'TICKTOK')


## TOKEN FOR IF-ELSE ##
t_START_CHECK	= r"(start\ check)"
t_END_CHECK		= r"(end\ check)"
t_RECHECK		= r"(recheck)"
t_RETREAT		= r"(retreat)"

tok_ifelse	= ('START_CHECK', 'END_CHECK', 'RECHECK', 'RETREAT',)



####### TOKENS FOR I/O #################
t_DISPLAY			= r"(display )"
t_RECEIVE			= r"(receive )"

tok_io = ('DISPLAY', 'RECEIVE')

#### TOKENS FOR MISC ####


def t_INITIAL_COMMENTS(t):
	r"\%\%[^\%]*\%\%"
	t.lexer.lineno += t.value.count('\n')
	return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# def t_foo_newline(t):
#     r'\n'
#     t.lexer.lineno += 1
# def t_bar_newline(t):
#     r'\n'
#     t.lexer.lineno += 1

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# t_EMPTY = r''
# tok_misc = ('EMPTY',)

# Error handling rule
def t_error(t):
    print("Illegal characters '%s' in line %i" % (t.value,t.lineno))
    # print(t.value)
    t.lexer.skip(1)
    exit()



tokens += tok_atoms
tokens += tok_io
tokens += tok_symbols
tokens += tok_mainfxn 
tokens += tok_fxn 
tokens += tok_loops
tokens += tok_ifelse
# tokens += tok_misc

print tokens


############ YACC ###########################
def p_program(t):
	'program : comment fxn main'


def p_fxn(t):
	'''fxn : fxnheader 
		| empty'''
	print "fxn detected"

def p_fxnheader(t):
	''' fxnheader : fxn_head FXNWITH LPAREN fxnargs RPAREN fxnret'''

def p_fxnargs(t):
	'''fxnargs : fxnarg
				| fxnarg COMMA fxnargs'''

def p_fxnarg(t):
	''' fxnarg : dtype identifier
				| empty'''

def p_fxnret(t):
	''' fxnret : FXNRETURN dtype
				| empty'''

def p_main(t):
    'main : main_head statements main_foot'
    # print "int main(void){"
    # # print t[2]
    # print "return 0;\n}"
    print "MAIN OK"

def p_statemets(t):
	'''statements : expr
				| var_dec statements
				| var_assign statements
				| comment statements
				| loops statements
				| ifelse statements
				| inout statements
				| empty'''

def p_inout(t):
	'''inout : DISPLAY identifier
			| RECEIVE identifier'''
	print "I/O detected"


def p_var_dec(t):
	'var_dec : dtype identifier'
	print "var dec"


def p_var_assign(t):
	'var_assign : identifier ASSIGN expr'
	print "var assign"

def p_comment(t):
	'''comment : COMMENTS comment
				| empty '''
	print "comments"

def p_expr(t):
    '''expr : LPAREN expr RPAREN
    		| expr OPERATION expr
    		| expr MOD expr
    		| intnum
    		| floatnum
    		| identifier 
    		| var_assign'''

    # print "int main(void){"
    print t[1]
    # print "return 0;\n}"
    # print t[-1]
    print "EXPR OK"

def p_expr2(t):
    '''expr2 : LPAREN expr2 RPAREN
    		| expr2 OPERATION expr2
    		| expr2 MOD expr2
    		| intnum
    		| floatnum
    		| identifier'''
    # print "int main(void){"
    # print "return 0;\n}"
    # print t[-1]
    print "EXPR2 OK"

def p_condition(t):
	'''condition : expr2 relation expr2
				|	var_assign'''
	print "condition ok"

def p_relation(t):
	'''relation : RELATIONAL
				| RELATIONALBIT'''
	print "relation ok"

def p_loops(t):
	'''loops : while
			| for '''
	pass

def p_for(t):
	'''for : START_LOOP LPAREN SINCE condition UNTIL condition DO TICKTOK identifier RPAREN RPAREN statements END_LOOP'''
	print "for loop"

def p_while(t):
	'''while : START_CYCLE LPAREN UNTIL condition RPAREN statements END_CYCLE'''
	print "while loop"

def p_ifelse(t):
	'''ifelse : START_CHECK LPAREN condition RPAREN statements otherif default END_CHECK'''
	print "if-else block"

def p_otherif(t):
	'''otherif : otherif RECHECK LPAREN condition RPAREN statements
				| empty'''

def p_default(t):
	'''default : RETREAT statements 
				| empty'''


def p_empty(p):
    'empty :'
    pass

def p_error(p):
	print p
	print "error"




#############################################
# dictionary of names
names = { }

data = []
source_name = sys.argv[1]
with open(source_name, 'r') as content_file:
    data = content_file.read()

lexer = lexy.lex()
lexer.input(data)

parser = yacc.yacc()
# Tokenize

# for tok in lexer:
# 	print(tok)

toks = []
parser.parse(data)
lexer.input(data)
# print "\n\n=========LEX TOKENS ==============="
# while True:

#     tok = lexer.token()
#     print tok
#     if not tok: 
#         break      # No more input
#     # print(tok.type, tok.value, tok.lineno)
#     toks.append(tok)
    # print(tok.type, tok.value, tok.lineno, tok.lexpos)

# print "\n\n============TOKS ================="
# for i in toks:
# 	print(i.value)
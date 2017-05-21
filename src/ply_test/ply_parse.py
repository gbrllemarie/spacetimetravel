##################################################
#
#	ply_parse.py
#
#	How to use ply_parse.py:
#
#	import ply_parse
#	status = ply_parse.startParse()
#	returns True if parsing if OK
#
#	if status != True:
#		exit() 		-- parsing fails
#
##################################################

import ply.lex as lexy
import sys, os
import ply.yacc as yacc

debug = 0
fxn_stack = []
fxn_list = []


########## LIST OF TOKENS ##########################
tokens = ('COMMENTS',  )

####### REGEX FOR TOKENS ###########################
wspace      	= r"[ \t]*"
ident_strip 	= r"([A-Za-z][A-Za-z0-9]*)"
ident 			= r"("+wspace+':'+ident_strip+':'+wspace+")"
t_identifier 	= r"("+wspace+ident+wspace+")"
integer			= r'[0-9]+'
t_intnum		= integer
t_floatnum		= r'('+integer+'\.'+integer+')'
t_dtype			= r"numeral|decimal|constellation|vacuum|starz|day" 
t_LTHAN			= r'<'
t_GTHAN			= r'>'

tok_atoms = ('identifier', 'intnum', 'floatnum',
	'dtype','LTHAN', 'GTHAN', )

#### TOKENS FOR SYMBOLS ###
t_DARKNESS		= r"(darkness)"
t_LIGHT			= r"(light)"
t_STRINGS		= r"(\"[^\"]*\")"
t_LPAREN  		= r'\('
t_RPAREN  		= r'\)'
t_OPERATION 	= r'(\+|-|\*|\/)'
t_RELATIONAL 	= r"\?((!?=)|(>=?)|(<=?))"
t_RELATIONALBIT = r"(\?(\&|\|))"
t_MOD			= r"(mod)"
t_COMMA			= r','
# t_PLUS    = r'\+'
# t_MINUS   = r'-'
# t_TIMES   = r'\*'
# t_DIVIDE  = r'/'
t_ASSIGN  = r"<-"

tok_symbols = ('OPERATION', 'ASSIGN', 'LPAREN','RPAREN',
	'RELATIONAL', 'RELATIONALBIT', 'MOD', 'COMMA', 'STRINGS', 'DARKNESS', 'LIGHT')

####### TOKENS FOR FUNCTIONS #####################

t_INITIAL_main_head = r"(ALPHA"+wspace+":time:)"
t_INITIAL_main_foot = r"(OMEGA"+wspace+":time:)"

tok_mainfxn = ('main_head', 'main_foot',)

t_INITIAL_fxn_head	= r"(activate)"
t_INITIAL_fxn_foot	= r"(deactivate)"
t_FXNRETURN 		= r"(returns)"
t_FXNWITH			= r"(with)"
t_FXNWARP			= r"(warp)"


t_fxn_returnval = r"(transmit)"

tok_fxn =  ('fxn_head', 'fxn_foot', 'fxn_returnval', 'FXNRETURN', 'FXNWITH',
	'FXNWARP')

####### TOKENS FOR STATEMENTS ######################
## TOKEN FOR LOOPS ##


t_START_CYCLE	= r"(start\ cycle)"
t_END_CYCLE		= r"(end\ cycle)"
t_START_LOOP	= r"(start\ loop)"
t_END_LOOP		= r"(end\ loop)"
t_UNTIL			= r"(until)"
t_SINCE			= r"(since)"
t_DO 			= r"(do)"
t_TICKTOK		= r"(tick|tock)"

tok_loops = ('START_CYCLE', 'END_CYCLE',
	'START_LOOP', 'END_LOOP', 'UNTIL', 'SINCE', 'DO', 'TICKTOK')


### TOKEN FOR IF-ELSE ###
t_START_CHECK	= r"(start\ check)"
t_END_CHECK		= r"(end\ check)"
t_RECHECK		= r"(recheck)"
t_RETREAT		= r"(retreat)"

tok_ifelse	= ('START_CHECK', 'END_CHECK', 'RECHECK', 'RETREAT',)



####### TOKENS FOR I/O #############################
t_DISPLAY			= r"(display\ |displayln\ )"
t_RECEIVE			= r"(receive\ )"

tok_io = ('DISPLAY', 'RECEIVE')

#### TOKENS FOR MISC ####


def t_INITIAL_COMMENTS(t):
	r"\%\%[^\%]*\%\%"
	t.lexer.lineno += t.value.count('\n')
	return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


# Error handling rule
def t_error(t):
    print "Error in line %i" % (t.lineno)
    print "Found these invalid character/s: ``%s''" % (t.value.split('\n')[0])
    t.lexer.skip(1)
    if debug == 0:
    	exit()


tokens += tok_atoms
tokens += tok_io
tokens += tok_symbols
tokens += tok_mainfxn 
tokens += tok_fxn 
tokens += tok_loops
tokens += tok_ifelse
tokens += ('newline',)
# tokens += tok_misc

# print tokens


############ YACC ##################################
def p_program(t):
	'program : comment fxns main'''

def p_fxns(t):
	'''fxns : fxn fxns
			| empty'''
	pass

def p_fxn(t):
	'''fxn : fxnheader statements fxnfooter comment'''
	# print "FXN OK"

def p_fxnheader(t):
	''' fxnheader : fxn_head identifier FXNWITH LPAREN fxnargs RPAREN fxnret'''
	if(len(fxn_stack) > 0):
		print "ERROR: Nested function in line "+str(t.lineno(2))
		exit()
	# print t[2]+"push"
	fname = t[2].strip(' ')
	if fname in fxn_list:
		print "ERROR: Function ''"+fname+"'' already defined in line "+str(t.lineno(2))
		exit()
	fxn_list.append(fname)
	fxn_stack.append(fname)
	pass
	

def p_fxnargs(t):
	'''fxnargs : fxnarg
				| fxnarg COMMA fxnarg
				| empty'''
	pass

def p_fxnarg(t):
	''' fxnarg : dtype identifier'''
	pass

def p_fxnret(t):
	''' fxnret : FXNRETURN dtype
				| empty'''
	pass

def p_fxnfooter(t):
	''' fxnfooter : fxn_foot identifier'''
	# print t[2]
	# print fxn_stack
	if fxn_stack[-1] != t[2].strip(' '):
		print "ERROR: Function names do not match ''"+t[2]+"'' in line "+str(t.lineno(2))
		exit()
	fxn_stack.pop()
	pass

def p_trans(p):
	''' trans : fxn_returnval identifier var_dec_array
				| fxn_returnval intnum
				| fxn_returnval floatnum'''
	# print "transmit"
	pass


def p_main(t):
    'main : main_head statements main_foot'
    # print "int main(void){"
    # print t[1].split(' ')
    # print "return 0;\n}"
    # print "MAIN OK"

def p_statemets(t):
	'''statements : expr newline statements
				| var_dec statements
				| var_assign statements
				| comment statements
				| loops statements
				| ifelse statements
				| inout  statements
				| warp statements
				| trans 
				| empty'''

def p_inout(t):
	'''inout : DISPLAY identifier var_dec_array
			| DISPLAY STRINGS
			| RECEIVE identifier var_dec_array'''
	# print "I/O detected"

# def p_identifier(t):
# 	'''identifier : ident'''

def p_var_dec(t):
	'''var_dec : dtype identifier var_dec_array'''
	# print "var dec"

def p_var_dec_array(t):
	'''var_dec_array : var_array
				| empty'''
	# print "var array"

def p_var_array(t):
	'''var_array : LTHAN intnum GTHAN
				| LTHAN identifier GTHAN'''


def p_var_assign(t):
	'var_assign : identifier var_dec_array ASSIGN expr'
	# print "var assign"

def p_bool_assign(t):
	''' bool_assign : DARKNESS
				| LIGHT'''

def p_comment(t):
	'''comment : COMMENTS comment
				| empty '''
	# print "comments"

def p_expr(t):
    '''expr : LPAREN expr RPAREN
    		| expr OPERATION expr
    		| expr MOD expr
    		| intnum
    		| floatnum
    		| identifier var_dec_array
    		| warp
    		| ticktock
    		| STRINGS
    		| bool_assign
    		| var_assign'''

    # print "int main(void){"
    # print "return 0;\n}"
    # print t[-1]
    # print "EXPR OK"

def p_expr2(t):
    '''expr2 : LPAREN expr2 RPAREN
    		| expr2 OPERATION expr2
    		| expr2 RELATIONAL expr2
    		| expr2 MOD expr2
    		| intnum
    		| floatnum
    		| warp
    		| ticktock
    		| bool_assign
    		| identifier var_dec_array'''
    # print "int main(void){"
    # print "return 0;\n}"
    # print t[-1]
    # print "EXPR2 OK"

def p_ticktock(t):
 	'ticktock : TICKTOK LPAREN identifier RPAREN'
 	# print "ticktok"

def p_condition(t):
	'''condition : expr2
				| expr2 RELATIONALBIT condition
				| var_assign
				| intnum'''
	# print "condition ok"

def p_loops(t):
	'''loops : while
			| for '''
	pass

def p_for(t):
	'''for : START_LOOP LPAREN SINCE condition UNTIL condition DO expr RPAREN statements END_LOOP'''
	# print "for loop"

def p_while(t):
	'''while : START_CYCLE LPAREN UNTIL condition RPAREN statements END_CYCLE'''
	# print "while loop"

def p_ifelse(t):
	'''ifelse : START_CHECK LPAREN condition RPAREN statements otherif default END_CHECK'''
	# print "if-else block"

def p_otherif(t):
	'''otherif : otherif RECHECK LPAREN condition RPAREN statements
				| empty'''
	# print "other block"

def p_default(t):
	'''default : RETREAT statements 
				| empty'''
	# print "default block"

def p_warp(p):
	'''warp : FXNWARP LPAREN identifier RPAREN LPAREN warpargs RPAREN'''
	# fname = p[3].strip(' ').replace(':', '')
	# print fname+"----"
	# if fxn_stack[-1] != 
	# 	print "ERROR: Function names do not match ''"+t[2]+"'' in line "+str(t.lineno(2))
	# 	exit()
	# fxn_stack.pop()
	# pass
	# print "warp"

def p_warpargs(p):
	'''warpargs : expr
				| expr COMMA warpargs
				| empty'''

def p_empty(p):
    'empty :'
    pass

def p_error(p):
	if p:
		print "Error detected in line "+str(p.lineno)
		print "Invalid character/s found: ``"+str(p.value)+"''"
	else:
		print "Error detected in EOF. ``OMEGA :time:'' must be the last line."
	if debug == 0:
		exit()


def startParse():
	data = []
	source_name = sys.argv[1]
	with open(source_name, 'r') as content_file:
	    data = content_file.read()

	lexer = lexy.lex()
	lexer.input(data)

	parser = yacc.yacc(debug=False)
	parser.parse(data,tracking=True)
	# print "Working"

	if debug == 1:
		toks = []
		tok1 =""
		lexer.input(data)
		while True:
		    tok = lexer.token()
		    if not tok: 
		        break      # No more input
		    toks.append(tok.value)
		    print tok
		    tok1 = tok1+tok.value
		print toks
		print tok1

	return True


if __name__ == "__main__":
	startParse()

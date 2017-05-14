# check if balance

import sys, os

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

def throwError(msg):
	print "ERROR on line "+str(lctr),
	print msg
	sys.exit()

if __name__ == '__main__':
	global slist
	slist = ['$']
	paren = []
	reserved = ['\%\%', '(',')', ':','activate', 'deactivate', 'ALPHA', 'OMEGA', 'start', 'end']
	reserved_open = ['\%\%', '(','activate','ALPHA','start']

	global lctr
	lctr = 0
	for line in source:
		lctr+=1
		try:
			for i in range(len(line)):
				if slist[-1] == reserved[0] and line[i] != '%':
					continue

				if line[i] == '%' and i < len(line)-1 and line[i+1] == '%':
					if slist[-1] == reserved[0]:
						del slist[-1]
						# print "popped %%"
						continue
					else:
						slist.append('\%\%')
						i+=1
						# print "added %%"
						continue
					

				if line[i] == ')':
					if slist[-1] == '(':
						del slist[-1]
						# print "popped ("
						continue
					else:
						throwError("closing parenthesis that was not opened")

				if line[i] == '(':
					slist.append('(')
					# print "added ("
					continue

				if slist[-1] == ':':
					if line[i] == ':':
						del slist[-1]
						# print "popped :"
						continue
					else:
						continue

				if line[i] == ':':
					slist.append(':')
					# print "added :"
					continue

				
				if str(line[i:i+5]) == 'ALPHA':
					slist.append('ALPHA')
					# print "added ALPHA"
					i+=5
					continue

				if str(line[i:i+5]) == 'OMEGA':
					if slist[-1] == 'ALPHA':
						del slist[-1]
						# print "popped ALPHA"
						i+=5
						continue
					else:
						throwError("detected an OMEGA not paired with ALPHA")

				if str(line[i:i+8]) == 'activate':
					slist.append('activate')
					# print "added activate"
					i+=8
					continue

				if str(line[i:i+10]) == 'deactivate':
					if slist[-1] == 'activate':
						del slist[-1]
						# print "popped activate"
						i+=10
						continue
					else:
						throwError("detected a deactivate not paired with activate")

				if str(line[i:i+5]) == 'start':
					slist.append('start')
					# print "added start"
					i+=5
					continue

				if str(line[i:i+3]) == 'end':
					if slist[-1] == 'start':
						del slist[-1]
						# print "popped start"
						i+=3
						continue
					else:
						throwError("detected an end not paired with a start")
		except:
			sys.exit()
			break

		if ':' in slist:
			throwError("closing ':' must be in same line")
	
	if(len(slist) > 1):
		#err = reserved_open.index(slist[-1])
		throwError("found an unpaired "+str(slist[-1]))
	else:
		print "all balanced"


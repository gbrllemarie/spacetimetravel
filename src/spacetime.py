
# compiler and runner program for spacetime travel source files
# should call ./main.py (parses input source code and outputs C translation)
# gcc compilation should happen here

# TODO: this entire thing (not important)
import os, sys

if len(sys.argv) != 3:
	print("Invalid arguments. Please follow the format:")
	print("python spacetime.py <inputfile> <outputfile>")
	exit()
raw_file = sys.argv[1]
c_file = sys.argv[2]
os.system('python main.py '+raw_file+'> '+c_file)

data = []
with open(c_file, 'r') as content_file:
	    data = content_file.read()

if 'Error' in data or 'error' in data:
	print data[data.find('rror')-1:-1]
	os.remove(c_file)


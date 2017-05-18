
from glob import glob
from os.path import basename, isfile

# define packages

__all__ = []

for file in glob("src/syntax/*.py"):
    if isfile(file):
        modname = basename(file)[:-3]
        if modname != "__init__":
            __all__.append(modname)

from syntax import *

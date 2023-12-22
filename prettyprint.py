import sys
from ast import *

with open(sys.argv[1], 'r') as f:
    file = ''
    for line in f.readlines(): file += line
    print(dump(parse(source = file, filename = sys.argv[1]), indent = 2))
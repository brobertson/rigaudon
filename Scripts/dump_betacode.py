#!/usr/bin/python

import sys
fileIn = open(sys.argv[1])
file_as_string = fileIn.read()
words = file_as_string.split()
for word in words:
	print word


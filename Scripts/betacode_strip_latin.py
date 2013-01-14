#!/usr/bin/python

import  re
import sys
is_greek = True 
fileIn = open(sys.argv[1])
file_as_string = fileIn.read()
words = file_as_string.split()
for word in words:
	for char in word:
		if char == '$':
			is_greek = True		
		if char == '&':
			is_greek = False
		if is_greek:
			sys.stdout.write(char)
	sys.stdout.write(' ')
#preprocess_re = re.compile('&.+?&')
#preprocess_re2 = re.compile('\$10.+?(\$|&)')
#out = preprocess_re.sub('FRF',file_as_string)
#out2 = preprocess_re2.sub('&',out)
#print out


#!/usr/bin/python
# coding: utf-8
from nltk.probability import FreqDist
import sys
from nltk.tokenize import RegexpTokenizer
from greek_tools import delete_non_greek_tokens
fdist = FreqDist()
text_array = []
for filename in sys.argv[1:]:
	print "opening ", filename, " ..."
	f = open(filename,'r')
	raw = f.read().decode('utf-8') 
	tokenizer = RegexpTokenizer('[\]\[)(·;\d><.,\s]+', gaps=True)
        lines = raw.split("\n")
        #print "lines: ", len(lines)
        for line in lines:
        #       print n, line.encode('utf-8') 
                line_tokens = tokenizer.tokenize(line)
                #for token in line_tokens:
                #       print token.encode('utf-8'), " | " 
                #n = n + 1
                text_array.append(line_tokens)

        #now try to match hyphenated lines with their 
        #correpsonding beginning lines
n = 0
for line in text_array:
	if len(line) > 0:
		if line[-1][-1] == '-':
			try:
                		line[-1] = line[-1][:-1] + text_array[n+1][0]
                        	text_array[n+1] = text_array[n+1][1:]
			except IndexError as e:
				print e
        n = n + 1
        #now flatten the 2d array
tokens = [item for sublist in text_array for item in sublist]
tokens = delete_non_greek_tokens(tokens)
for token in tokens:
	fdist.inc(token)

print "most common: ", fdist.max().encode('utf-8')		
for item in fdist.keys():
	print item.encode('utf-8'), fdist.freq(item)

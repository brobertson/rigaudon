#!/usr/bin/env python
import unicodedata 
import codecs
import sys

#check for proper input
if (len(sys.argv) != 2):
	exit("Usage: unicode_debug [filename]")
try:
	f = codecs.open(sys.argv[1], encoding="utf-8")
except IOError:
	exit('cannot open file "' +  sys.argv[1] + '"')

#make report
print "unicode dump for " + f.name

for line in f:
	print line.encode('utf-8')
	for word in line.split():
		print '\t' + word.encode('utf-8')
		for char in word:
			print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"

def lowerStripAccents(word):
	wordOut = []
	sigma = unichr(963)
	word = word.lower()
	for char in word:
		cat = unicodedata.category(char)
		if (cat[0] == 'L'):
			charNum = ord(char)
			if (charNum == 962):
				wordOut.append(sigma)
			else:
				wordOut.append(char)
	return u''.join(wordOut)



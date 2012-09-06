import unicodedata 
import codecs

def dummyTempData():
	print "    - 2011-05-24 11:11:11.111111"
	print "    - 2011-05-24 11:11:11.111111"

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

x = 1
f = codecs.open("/Users/brobertson/forms-u.txt", encoding="utf-8")
for line in f:
	try:
   	 number,word = line.split('\t')
	#  	 number = (number + 1)
	# out = int(number)
   	 word = word.rstrip()
   	 print "  - - ", int(number) #+ 1
   	 unicode.rstrip(number)
   	 print "    - ", word.encode('utf-8')
	#  	 print "  - ", word.lower().encode('utf-8')
   	 #print word
   	 print  "    - ", lowerStripAccents(word).encode('utf-8')
   	 dummyTempData()
   	 print
	#  	 for char in word:
	#  	 	print '%04x' % ord(char), ord(char), unicodedata.category(char), unicodedata.name(char)
	except ValueError:
		pass
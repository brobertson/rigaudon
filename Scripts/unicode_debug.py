#!/usr/bin/env python
import unicodedata
import codecs
import sys
from greek_tools import recursive_combine, can_combine



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
        x = -1
        output = u''
        while x <  len(word) -1:
            x = x + 1
            char = word[x]
            print '\t\t'  + unicodedata.name(char).encode('utf-8') + u" (" + unicodedata.category(char).encode('utf-8') + u")"
            set_of_chars = char
            for char in word[x+1:]:
                try:
                    if unicodedata.category(char) == 'Mn':
                        print '\t\t appending'  + unicodedata.name(char).encode('utf-8') + u" (" + unicodedata.category(char).encode('utf-8')
                        set_of_chars = set_of_chars + char
                        x = x + 1
                    else:
                        break
                except:
                    pass
            if len(set_of_chars) > 1:
                a = recursive_combine(set_of_chars,'')
                print '\t\t combined', a[0]
                print '\t\t rejecte3d', a[1]
                output = output + a[0] + a[1]
            else:
                output = output + char
        print output



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



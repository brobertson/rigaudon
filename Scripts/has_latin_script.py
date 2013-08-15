#!/usr/bin/python
# vim: set fileencoding=UTF-8 :
def is_latin_text(url):
	import urllib2
	import sys
	f = urllib2.urlopen(url)
	for line in f:
    		if u'a' in line.decode('utf-8'):
        		return True
	return False
import sys
#print 'testing', sys.argv[1], ' Is latin text?'
print is_latin_text("http://www.archive.org/download/" + sys.argv[1] +  "/" + sys.argv[1] + '_djvu.txt')
        


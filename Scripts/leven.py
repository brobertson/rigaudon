#!/usr/bin/python
# coding: utf-8
def transIn(input):
	import unicodedata
#	input = u'καθάπερ'
	inputD = unicodedata.normalize('NFD',input)
#	for char in inputD:
 #                       print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"
#	print ""
	smooth_breathing = unicode(u"\N{COMBINING COMMA ABOVE}")
      	rough_breathing = unicode(u"\N{COMBINING REVERSED COMMA ABOVE}")
      	circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
      	acute_accent = unicode(u"\N{COMBINING ACUTE ACCENT}")
      	grave_accent = unicode(u"\N{COMBINING GRAVE ACCENT}")
	iota_subscript = unicode(u"\N{COMBINING GREEK YPOGEGRAMMENI}")
	other_circumflex = unicode(u"\N{COMBINING CIRCUMFLEX ACCENT}")
	intab = u'' + smooth_breathing + rough_breathing + circumflex + acute_accent + grave_accent + iota_subscript 
        smooth_breathing_replacement=u'\u21b2'#u')'
	rough_breathing_replacement=u'\u21b1'#u'('
	circumflex_replacement=u'\u2194'#u'~'
	acute_accent_replacement=u'\u2197'#u'/'
	grave_accent_replacement=u'\u2196'#u'\\'
	iota_subscript_replacement=u'\u2193'#u'|'
	outtab= u'' + smooth_breathing_replacement + rough_breathing_replacement + circumflex_replacement + acute_accent_replacement + grave_accent_replacement + iota_subscript_replacement 
	#outtab = u")(~/\|"
        trantab = dict((ord(a), b) for a, b in zip(intab, outtab))
	return inputD.translate(trantab)

def GreekUnicodeDdiffRatio(wordOne, wordTwo):
	wordOneTrans = transIn(wordOne)
	wordTwoTrans = transIn(wordTwo)
	import unicodedata 
#	for char in wordOne:
 #                       print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"
  #      print ""
#	for char in wordTwo:
 #                       print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"
  #      print ""
	import difflib
#	print "difflib: ",
#	print str(difflib.SequenceMatcher(None, wordOneTrans, wordTwoTrans).ratio())
	import Levenshtein
 	lev =  Levenshtein.ratio(wordOneTrans, wordTwoTrans)
#	print "lev: ",
#	print str(lev)
	return lev
#
import sys

def main():
	print GreekUnicodeDdiffRatio( sys.argv[1].decode('utf-8'),  sys.argv[2].decode('utf-8'))

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
#import difflib
#print difflib.SequenceMatcher(None,  u'αὕτη', u'αύτη').ratio()

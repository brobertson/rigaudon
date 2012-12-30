#!/usr/bin/python
# coding: utf-8
import codecs
import nltk
import unicodedata
import re
import sys
from nltk.tokenize import RegexpTokenizer

debug =False 

def clean_word(word):
	import unicodedata
        circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
        other_circumflex = unicode(u"\N{COMBINING CIRCUMFLEX ACCENT}")
	replacement_char = unicode(u"\N{REPLACEMENT CHARACTER}")
	under_dot =  unicode(u"\N{COMBINING DOT BELOW}")
	greek_koronis =  unicode(u"\N{GREEK KORONIS}")
	apostrophe =  unicode(u"\N{APOSTROPHE}")
	myre = re.compile(ur'[|\^\?#-.!,;·\d@}{"\$><_]+',re.UNICODE)
        word = word.replace(other_circumflex,circumflex)
	#word = word.replace('_',' ')
	word = myre.sub('',word)
	myre2 = re.compile(ur'[\u0000-\u001f]',re.UNICODE)
        word = myre2.sub('',word)
	#word = re.sub(ur'['+replacement_char+ur'-.!,;]', '', word)
	word = word.replace(replacement_char,'')
	#word = word.replace(greek_koronis,apostrophe)
	#word = word.replace(u"-",'')
        word = unicodedata.normalize('NFD',word)
	return word


f = codecs.open(sys.argv[1],'r',encoding='utf-8')
raw = f.read()
#out = raw.split()
#Avoid instance where a hyphenated word has a space after the hyphen
#dashspace_re = re.compile(ur'- +',re.UNICODE)
#raw = dashspace_re.sub('',raw)
#sometimes words are joined by underscore
#raw = raw.replace('_',' ')
#Remove certain supplied texts
myre3 = re.compile(ur'\[1&.+\]1',re.UNICODE)
raw = myre3.sub('',raw)
#myre4 = re.compile(ur'\[2.+]2',re.UNICODE)
#raw = myre3.sub('',raw)
#preprocess_re = re.compile(ur'-\d+',re.UNICODE)
#raw = preprocess_re.sub('',raw)
#myre2 = re.compile(ur'[\u0000-\u001f]',re.UNICODE)
#raw = myre2.sub('',raw)
tokenizer = RegexpTokenizer('\s', gaps=True)
#tokenizer = RegexpTokenizer('(\s+)', gaps=True)
out = tokenizer.tokenize(raw)
#print "total tokens: ", len(out)
n = 0
if (debug):
	print "RAW TOKENS:"
	for item in out:
		print item.encode('utf-8')
#	for letter in item:
#		print letter.encode('unicode-escape')

stripped = []
under_dot =  unicode(u"\N{COMBINING DOT BELOW}")
exclude = re.compile(ur"]",re.UNICODE)
exclude = re.compile(ur"[-\d_><?\[\]#@" + under_dot + ur"\ufffd]",re.UNICODE)
for item in out:
        if not bool(exclude.search(item)):
                stripped.append(item)
if (debug):
	print "STRIPPED RAW TOKENS:"
	for item in stripped:
		print "SR", item.encode('utf-8')

out_clean = [clean_word(item) for item in stripped]

if (debug):
	print "CLEAN TOKENS:"
	for item in out_clean:
		print "CL",item.encode('utf-8')

out_clean = sorted(out_clean)
out_clean = list(set(out_clean))
out_clean = sorted(out_clean)
#print "unique tokens: ", len(out_clean)
#    for char in item:
#                print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"
if (debug):
	print "DONE TOKENS:"
for item in out_clean:
	if (debug):
		print  "DO",
	print item.encode('utf-8')

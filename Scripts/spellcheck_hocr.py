#!/usr/bin/python
# coding: utf-8
from gamera.core import init_gamera
init_gamera()
import lxml
from lxml import etree
import sys
import re
from greek_tools import dump, split_text_token
import codecs
import unicodedata
spellcheck_dict = {}
with codecs.open(sys.argv[1],'r','utf-8') as spellcheck_file:
	for line in spellcheck_file:
		line = line.strip()
		pair = line.split(',')
#		dump(pair[0])
#		print 
#		dump(unicodedata.normalize('NFD',pair[0]))
#		print
#		dump(pair[1])
#		print
#		print
		spellcheck_dict[unicodedata.normalize('NFD',pair[0])] = unicodedata.normalize('NFD',pair[1])
print "dictionary length: ", len(spellcheck_dict)
print "reading file ", sys.argv[2]
fileIn = codecs.open(sys.argv[2],'r','utf-8')
treeIn = etree.parse(fileIn)
root = treeIn.getroot()
hocr_word_elements = treeIn.xpath("//html:span[@class='ocr_word'] | //span[@class='ocr_word']",namespaces={'html':"http://www.w3.org/1999/xhtml"})
for word_element in hocr_word_elements:
   #print word_element.text
   try:
      word = unicodedata.normalize('NFD',word_element.text)
   except TypeError:
      word = unicodedata.normalize('NFD',unicode(word_element.text))
   #dump(word)
   parts = split_text_token(word)
   #for part in parts:
	#print '\t',part
   try:
      #print "trying to check", parts[1]
      error_word = parts[1]
      parts = (parts[0], spellcheck_dict[parts[1]], parts[2])
      print "replaced", error_word, "with", parts[1]
      dump(error_word)
      print 
      dump(parts[1])
    #  dump(parts[1])
   except KeyError:
      #print "no check"
      pass
 #  print parts[0]+parts[1]+parts[2]
   word_element.text = parts[0]+parts[1]+parts[2]
out_file = codecs.open(sys.argv[3],'w','utf-8')
out_file.write(etree.tostring(treeIn.getroot(), xml_declaration=True))
out_file.close()


#!/usr/bin/python
# coding: utf-8
#from gamera.core import init_gamera
#init_gamera()
import lxml
from lxml import etree
import sys
import re
from greek_tools import dump, split_text_token
import codecs
import os
import unicodedata
import HTMLParser
html_parser = HTMLParser.HTMLParser()
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
print "reading dir ", sys.argv[2]
dir_in = sys.argv[2]
dir_out = sys.argv[3]
if  not os.path.isdir(dir_in) or not os.path.isdir(dir_out):
        print "usage: spellcheck.csv dir_in dir_out"
        exit()
        
for file_name in os.listdir(dir_in):
        if file_name.endswith('.html'):
                simplified_name = file_name
                if file_name.startswith('output-'):
                        simplified_name = file_name[7:]
                print simplified_name
                name_parts = simplified_name.split('_')
                print name_parts
                simplified_name = name_parts[0] + '_' + name_parts[1] + '.html'
                fileIn_name = os.path.join(dir_in,file_name)
                fileOut_name = os.path.join(dir_out,simplified_name)
                fileIn= codecs.open(fileIn_name,'r','utf-8')
                #fileOut = codecs.open(fileOut_name, 'w','utf-8')
                fileOut = open(fileOut_name,'w')
                print "checking", fileIn_name, "sending to ", fileOut_name
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
                      word_element.set('data-pre-spellcheck',word)
                    #  dump(parts[1])
                   except KeyError:
                      #print "no check"
                      pass
                 #  print parts[0]+parts[1]+parts[2]
                   word_element.text = parts[0]+parts[1]+parts[2]
                fileOut.write(html_parser.unescape(etree.tostring(treeIn.getroot(), encoding="UTF-8", method='html', xml_declaration=False)))
                fileOut.close()


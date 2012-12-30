#!/usr/bin/python
# coding: utf-8
import sys
import difflib
import leven
import codecs
import unicodedata
from  greek_tools import dump, delete_non_greek_tokens, is_greek_char, is_greek_string

teubner_serif_weights = [
	['replace', '|', unicode(u"\N{GREEK SMALL LETTER IOTA}"),1],
	['replace', unicode(u"\N{RIGHT SINGLE QUOTATION MARK}"),  unicode(u"\N{APOSTROPHE}"),1],
	['replace',  ur')',  ur'/',1],
	['replace',  ur'(',  ur'/',1],
	['replace', ur'ΟοO0o', ur'ΟοO0o',1],
	['replace',ur'Λλ',ur'Λλ',1],
	['replace',ur'A',ur'Α',1],
	['replace',ur'BβΒ',ur'BβΒ',1],
	['replace',ur'Z',ur'Ζ',1],
	['replace',ur'H',ur'Η',1],
	['replace',ur'I',ur'Ι',1],
	['replace',ur'li1',ur'ιΙ',1],
	['replace',ur'M',ur'Μ',1],
	['replace',ur'N',ur'Ν',1],
	['replace',ur'Pp',ur'Ρρ',1],
	['replace',ur'ϲϹ',ur'σςΣ',1],
	['replace',ur'c',ur'σς',1],
	['replace',ur'T',ur'Τ',1],
	['replace',ur'Uu',ur'υ',1],
	['replace',ur'Y',ur'Υ',1],
	['replace',ur'E',ur'Ε',1],
	['replace',ur'Z',ur'Ζ',1],
	['replace',ur'K',ur'Κ',1],
	['replace',ur'a',ur'α',1],
	['replace',ur'ΛΑ',ur'ΛΑ',1],
	['insert',ur'*',ur'\(\)|~',1],
	['delete',ur'()|~',ur'*',1],
	['replace',ur'()|~',ur'()|~',1]
	]

debug = False


def weight_for_leven_edits(wordFrom, wordTo, edits, weight_rules):
		
	debug = False 
	if (debug):
		print
		print
		print "trying weight"
		print "word in: " 
		dump(wordFrom)
		print
		print "word to: "
		dump(wordTo)
	cumulative_weight = 0
	for edit in edits:
		edit_weight = 0
		if (debug): 
			print edit
		(command, char_num_in_word_one, char_num_in_word_two) = edit
		if  (char_num_in_word_one > (len(wordFrom) - 1)):
                	char_in_word_one = '' 
                else:
                        char_in_word_one = wordFrom[char_num_in_word_one]
		if (char_num_in_word_two > (len(wordTo) - 1)):
                	char_in_word_two = ''
                else:
                        char_in_word_two = wordTo[char_num_in_word_two]
		if (debug):
			print '\t',command  
			if char_in_word_one:
				print '\t', unicodedata.name(char_in_word_one)
			else:
				print '\tx'
			if char_in_word_two:
				print '\t', unicodedata.name(char_in_word_two)
			else:
				print '\tx'
		if (command == 'replace'):
			edit_weight = 8 
		elif (command == 'delete'):
			edit_weight = 10
		elif (command == 'insert'):
			edit_weight = 13
		else:
			raise ValueError('unknown Levenshtein edit operation: ' + command)
		for weight_rule in weight_rules:
			if (weight_rule[0] == command) and (weight_rule[1] == '*' or char_in_word_one in weight_rule[1])  and (weight_rule[2] == '*' or char_in_word_two in weight_rule[2]):
				if (debug):
					print '\t weight rule applied:'
					print '\t', weight_rule
				edit_weight = weight_rule[3]
				break
		if (debug):
			print '\tweight: ',edit_weight
		cumulative_weight += edit_weight
	return cumulative_weight

	
		

def spellcheck_url(dict_file, url):
	from urllib import urlopen
	import nltk
	from nltk.tokenize import RegexpTokenizer
	raw = urlopen(url).read().decode('utf-8')
	n = 0
	tokenizer = RegexpTokenizer('[)(·;\d><.,\s]+', gaps=True)
	lines = raw.split("\n")
	text_array = [] 
	#print "lines: ", len(lines)
	for line in lines:
	#	print n, line.encode('utf-8') 
		line_tokens = tokenizer.tokenize(line)
		#for token in line_tokens:
		#	print token.encode('utf-8'), " | " 
		#n = n + 1
		text_array.append(line_tokens)
	
	#now try to match hyphenated lines with their 
	#correpsonding beginning lines
	n = 0
	for line in text_array[:-2]:
		#print line
		if len(line) > 0:
#			print line[-1].encode('utf-8')
			if line[-1][-1] == '-':
				line[-1] = line[-1][:-1] + text_array[n+1][0]
				text_array[n+1] = text_array[n+1][1:]
		n = n + 1
	#now flatten the 2d array
	tokens = [item for sublist in text_array for item in sublist]
	#now remove tokens that are not Greek
	print "printing tokens"
	for token in tokens:
		for word in tokens:
			print word.encode('utf-8')
	tokens = delete_non_greek_tokens(tokens)
	print tokens 
	vocab = sorted(set(tokens))
	print "vocab of ", len(vocab), " words"
	word_dicts  = makeDict(dict_file)
        (dict_words, words_clean)  = word_dicts
        for wordIn in vocab:
                wordIn = preprocess_word(wordIn)
                output_words = getCloseWords(wordIn, word_dicts, teubner_serif_weights, threshold=5)
                #print
                #print wordIn, ":"
		if len(output_words) > 0 and output_words[0][1] == 0:
			print "*"
		else:
			for word,lev_distance,n,w,junk1,junk2  in output_words[:5]:
                       		print words_clean[word].encode('utf-8'), w, lev_distance, n	
				#dump(word)
				if (lev_distance == 0):
					break
def makeDict(fileName):
	words_transformed = []
	words_clean = {} 
	n = 0
	mine = codecs.open( fileName,'r', 'utf-8')
	for line in mine:
		#wordsInLine = line.split()
		#print len(wordsInLine)
		#for word in wordsInLine:
		line = line.rstrip('\r\n')
		word = preprocess_word(line)
		thisWord = leven.transIn(word)	
		words_transformed.append(thisWord)
		words_clean[thisWord] = word
	
	print "dictionary: ",len(words_transformed), " words."
	#for word in words_transformed:
	#	dump(word)
	#	print
	#	dump(words_clean[word])
	#	print
	#	print
	return (words_transformed, words_clean)

def preprocess_word(word):
	#ensures that word is in Python's NFD, and checks for bogus circumflexes that don't compose properly
	word = word.replace(' ','')
	import unicodedata
        circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
        other_circumflex = unicode(u"\N{COMBINING CIRCUMFLEX ACCENT}")
	greek_koronis =  unicode(u"\N{GREEK KORONIS}")
        apostrophe =  unicode(u"\N{APOSTROPHE}")
        word = word.replace(other_circumflex,circumflex)
	word = word.replace(greek_koronis,apostrophe)
	word = unicodedata.normalize('NFD',word)
	return word

def unicode_test(word):
	import unicodedata
	print 
	print
	circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
        other_circumflex = unicode(u"\N{COMBINING CIRCUMFLEX ACCENT}")
	word = word.replace(other_circumflex,circumflex)
	print "*** ", word, ": "  
	print "Input: "
	dump(word)
	nfd = unicodedata.normalize('NFD',word)
	if not word == nfd:
		print "The decomposed verison is NOT the same: ",
		print nfd
		dump(nfd)
	else:
		print "(NFD is the same)"
	try:
		cfd = unicodedata.normalize('NFC',word)
	except Error as foo:
		print foo
		
	print "CFD: ",cfd
	dump(cfd)
		
def getCloseWords(wordIn, word_dicts, rules, threshold=2, fast=True):
	import Levenshtein
	#out = difflib.get_close_matches('ἐστιν',words)
	(dict_words, words_clean) = word_dicts
	#print "word in:"
	#print dump(wordIn)
	#wordIn = preprocess_word(wordIn)
	#print "word in pp:"
	#print dump(wordIn)
	wordInTrans = leven.transIn(wordIn)
	print
	print wordInTrans.encode('utf-8'), "(", wordIn.encode('utf-8'),")"
	#dump(wordInTrans)
	output_words = []
	n = 0 
	#print "Now comparing to..."
	for word in dict_words:
		#print u"*****" + words_clean[n]	
		#print "word into comparison:"
		#print dump(word)
		lev_distance =  Levenshtein.distance(wordInTrans, word)#difflib.SequenceMatcher(None, word, wordInTrans).ratio()
		#print "distance: ",
		#print ratio
		if lev_distance <= threshold:
			edits =   Levenshtein.editops(wordInTrans, word)
			w = weight_for_leven_edits(wordInTrans,word,edits,rules)
			output_words.append((word,lev_distance,len(edits),w,'xxx','yyy'))
			if (lev_distance == 0) and (fast == True):
				#In the case of an exact match, cut the search short
                                #We might have got some close matches ahead of time, so this will not create a complete list
                                return sorted(output_words, key=lambda word: int(word[3]))
		n = n + 1
	return sorted(output_words, key=lambda word: word[3])

def main():
	fileName =  sys.argv[1].decode('utf-8')	
	wordsIn =  sys.argv[2:]
	word_dicts = makeDict(fileName)
	(dict_words, words_clean) = word_dicts
	rule_regexes = compile_weight_rules_to_regexes(teubner_serif_weights)
	for wordIn in wordsIn:
		wordIn = wordIn.decode('utf-8')
		wordIn = preprocess_word(wordIn)
		output_words = getCloseWords(wordIn, word_dicts, rule_regexes, threshold=6)
		print
		print wordIn, ":"
		for word,lev_distance,number,weighted_lev_distance,edits in output_words[:5]:
			print words_clean[word], weighted_lev_distance, lev_distance, len(edits)
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   #main()
	import sys
	spellcheck_url(sys.argv[1], sys.argv[2])
	

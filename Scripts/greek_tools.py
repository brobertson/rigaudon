#!/usr/bin/python
# -*- coding: utf8 -*- 
import unicodedata

def memoize(f):
    cache= {}
    def memf(*x):
        if x not in cache:
            cache[x] = f(*x)
        return cache[x]
    return memf


def dump(stringIn):
        for char in stringIn:
                try:
                        print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"
                except ValueError:
                        print '\t\t' + char.encode('unicode-escape')
@memoize
def is_greek_char(char):
                import re
                return bool(re.match(ur'([\u0373-\u03FF]|[\u1F00-\u1FFF]|\u0300|\u0301|\u0313|\u0314|\u0345)',char,re.UNICODE))

@memoize
def is_greek_capital(char):
	import re
	return bool(re.match(ur'([\u0391-\u03A9])',char,re.UNICODE))

@memoize
def is_uc_word(string_in):
	count = 0
	threshold = 0.7
        count = 0
        if string_in == None or len(string_in) < 1:
                return False
        for char in string_in:
                if is_greek_capital(char):
                        count = count + 1
        factor = float(count) / float(len(string_in))
        #print "factor: ", factor
        if factor > threshold:
                return True
        else:
                return False

@memoize
def is_number(string_in):
    #for the purposes of OCR, we include Latin capital O and Latin capital I as digits :-)
    #the point here isn't to clean, but rather to discern if, in a Latin OCR output context, the word is likely a number
    import re
    allowed_punct='\.' #what punctuation do you want to include as part of a number?
    allowed_chars = 'OIi'
    return bool(re.match('[\d' + allowed_chars + allowed_punct + ']+', string_in))

@memoize
def is_greek_string(string_in):
	import string,re
	regex = re.compile('[%s]' % re.escape(string.punctuation + u'—·' + u'0123456789'))
        greekness_threshold = 0.7
        #print "String to test for greekness: ", string_in.encode('utf-8')
        string_in = regex.sub('',string_in,re.UNICODE)
	#print "cleaned string to test: ", string_in.encode('utf-8')
        count = 0
        if string_in == None or len(string_in) < 1:
                return False
        for char in string_in:
                if is_greek_char(char):
                        count = count + 1
        factor = float(count) / float(len(string_in))
        #print "factor: ", factor
        if factor > greekness_threshold:
                return True
        else:
                return False


#@memoize
def delete_non_greek_tokens(tokens):
        tokens_out = []
        for token in tokens:
                if is_greek_string(token):
                        #print token.encode('utf-8'), " GREEK"
                        tokens_out.append(token)
        #        else:
                        #print token.encode('utf-8'), " LATIN"
        return tokens_out

def split_text_token(stringIn):
	import re
	word_parts = re.match(ur'(^[\[\("]*)(.*?)([.,!?;†·:〉\]\)\d]*$)',stringIn,re.UNICODE)
   	try:
      		parts = word_parts.groups()
	except AttributeError:
		parts = ('',stringIn,'')
	return parts

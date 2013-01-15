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
def is_greek_string(string_in):
	import string,re
	regex = re.compile('[%s]' % re.escape(string.punctuation + u'—·' + u'0123456789'))
        greekness_threshold = 0.7
        print "String to test for greekness: ", string_in.encode('utf-8')
        string_in = regex.sub('',string_in)
	print "cleaned string to test: ", string_in.encode('utf-8')
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


@memoize
def delete_non_greek_tokens(tokens):
        tokens_out = []
        for token in tokens:
                if is_greek_string(token):
                        #print token.encode('utf-8'), " GREEK"
                        tokens_out.append(token)
        #        else:
                        #print token.encode('utf-8'), " LATIN"
        return tokens_out


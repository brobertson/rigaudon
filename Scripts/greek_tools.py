#!/usr/bin/python
import unicodedata
def dump(stringIn):
        for char in stringIn:
                try:
                        print '\t\t' + unicodedata.name(char) +" (" + unicodedata.category(char) + ")"
                except ValueError:
                        print '\t\t' + char.encode('unicode-escape')

def is_greek_char(char):
                import re
                return bool(re.match(ur'([\u0373-\u03FF]|[\u1F00-\u1FFF]|\u0300|\u0301|\u0313|\u0314|\u0345)',char,re.UNICODE))


def is_greek_string(string):
        greekness_threshold = 0.7
        #print "String to test for greekness: ", string.encode('utf-8')
        count = 0
        if string == None:
                return False
        for char in string:
                if is_greek_char(char):
                        count = count + 1
        factor = float(count) / float(len(string))
        #print "factor: ", factor
        if factor > greekness_threshold:
                return True
        else:
                return False



def delete_non_greek_tokens(tokens):
        tokens_out = []
        for token in tokens:
                if is_greek_string(token):
                        #print token.encode('utf-8'), " GREEK"
                        tokens_out.append(token)
        #        else:
                        #print token.encode('utf-8'), " LATIN"
        return tokens_out


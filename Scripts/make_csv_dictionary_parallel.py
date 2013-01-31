#!/usr/bin/python
# -*- coding: utf8 -*- 
import codecs


def Dehyphenate(lines):
	import nltk
        from nltk.tokenize import RegexpTokenizer
        n = 0
        tokenizer = RegexpTokenizer('[)(·;\d><.,\s]+', gaps=True)
        #lines = raw.split("\n")
        text_array = []
#        print "lines: ", len(lines)
        for line in lines:
  #              print n, line.encode('utf-8') 
                line_tokens = tokenizer.tokenize(line)
  #              for token in line_tokens:
  #                     print token.encode('utf-8'), " | " 
                n = n + 1
                text_array.append(line_tokens)
 #       print "Done printing lines"
        #now try to match hyphenated lines with their 
        #correpsonding beginning lines
        n = 0
        for line in text_array[:-2]:
   #             print line
                if len(line) > 0:
    #                    print "last token: ", line[-1].encode('utf-8')
                        if line[-1][-1] == '-':
                                next_non_empty_line = n+1
                                while (len(text_array[next_non_empty_line]) < 1):
					next_non_empty_line += 1 
     #                           print "line is ", n, "next non empty is: ", next_non_empty_line
      #                          print "it looks like ",text_array[next_non_empty_line], " and has size", len(text_array[next_non_empty_line])
				line[-1] = line[-1][:-1] + text_array[next_non_empty_line][0]
                                text_array[next_non_empty_line] = text_array[next_non_empty_line][1:]
#				print "\tadded to form ",line[-1].encode('utf-8')
                n = n + 1
        #now flatten the 2d array
        tokens = [item for sublist in text_array for item in sublist]
        #now remove tokens that are not Greek
#        print "printing tokens"
#        for token in tokens:
#                for word in tokens:
#                        print word.encode('utf-8')
        return tokens

"""
Given a list of tokens, return a list of tuples of
titlecased (or proper noun) tokens and a count of '1'.
Also remove any leading or trailing punctuation from
each token.
"""
def Map(L):
  import string
  al = set(string.letters)
  results = []
  for w in L:
    # True if w contains non-alphanumeric characters
    if len(set(w) & al) ==  0:
      w = sanitize (w)

    # True if w is a title-cased token
#    if w.istitle():
      results.append ((w, 1))

  return results

"""
Group the sublists of (token, 1) pairs into a term-frequency-list
map, so that the Reduce operation later can work on sorted
term counts. The returned result is a dictionary with the structure
{token : [(token, 1), ...] .. }
"""
def Partition(L):
  tf = {}
  for sublist in L:
    for p in sublist:
      # Append the tuple to the list in the map
      try:
        tf[p[0]].append (p)
      except KeyError:
        tf[p[0]] = [p]
  return tf

"""
Given a (token, [(token, 1) ...]) tuple, collapse all the
count tuples from the Map operation into a single term frequency
number for this token, and return a final tuple (token, frequency).
"""
def Reduce(Mapping):
  return (Mapping[0], sum(pair[1] for pair in Mapping[1]))



import sys
from multiprocessing import Pool
"""
If a token has been identified to contain
non-alphanumeric characters, such as punctuation,
assume it is leading or trailing punctuation
and trim them off. Other internal punctuation
is left intact.
"""
def sanitize(w):
  import string,re
  regex = re.compile('[%s]' % re.escape(string.punctuation + u'〉〈“‘†”—·' + u'0123456789'))
  w = regex.sub('',w)
  # Strip punctuation from the front
  #while len(w) > 0 and not w[0].isalnum():
  #  w = w[1:]

  # String punctuation from the back
  #while len(w) > 0 and not w[-1].isalnum():
  #  w = w[:-1]

  return w
"""
Load the contents the file at the given
path into a big string and return it.
"""
def load(path):

  word_list = []
  f = codecs.open(path, "r","utf-8")
  for line in f:
    word_list.append (line)
  #print (''.join(word_list)).split ()
  # Efficiently concatenate Python string objects
  #return (''.join(word_list)).split ()
  return Dehyphenate(word_list)
"""
A generator function for chopping up a given list into chunks of
length n.
"""
def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

"""
Sort tuples by term frequency, and then alphabetically.
"""
def tuple_sort (a, b):
  if a[1] < b[1]:
    return 1
  elif a[1] > b[1]:
    return -1
  else:
    return cmp(a[0], b[0])

if __name__ == '__main__':

  if (len(sys.argv) != 3):
    print "Program requires path to file for reading and number of processes!"
    sys.exit(1)

  # Load file, stuff it into a string
  text = load (sys.argv[1])
  num_processes = int(sys.argv[2])
  # Build a pool of n processes
  pool = Pool(processes=num_processes,)

  # Fragment the string data into n chunks
  partitioned_text = list(chunks(text, len(text) / num_processes))

  # Generate count tuples for title-cased tokens
  single_count_tuples = pool.map(Map, partitioned_text)

  # Organize the count tuples; lists of tuples by token key
  token_to_tuples = Partition(single_count_tuples)

  # Collapse the lists of tuples into total term frequencies
  term_frequencies = pool.map(Reduce, token_to_tuples.items())

  # Sort the term frequencies in nonincreasing order
  term_frequencies.sort (tuple_sort)

  for pair in term_frequencies:
    print pair[0].encode('utf-8') +  "," +  str(pair[1]).encode('utf-8')


#!/usr/bin/python
# coding: utf-8
import sys
import difflib
import leven
import codecs
import unicodedata
from greek_tools import dump, delete_non_greek_tokens, is_uc_word, is_greek_char, is_greek_string

teubner_serif_weights = [
    ['replace', '|', unicode(u"\N{GREEK SMALL LETTER IOTA}"), 1],
    ['replace', unicode(u"\N{RIGHT SINGLE QUOTATION MARK}"),
     unicode(u"\N{APOSTROPHE}"), 1],
    ['replace', ur')', ur'/', 1],
    ['replace', ur'(', ur'/', 1],
    ['replace', ur'ΟοO0o', ur'ΟοO0o', 2],
    ['replace', ur'Λλ', ur'Λλ', 1],
    ['replace', ur'A', ur'Α', 1],
    ['replace', ur'BβΒ', ur'BβΒ', 1],
    ['replace', ur'Z', ur'Ζ', 1],
    ['replace', ur'H', ur'Η', 1],
    ['replace', ur'I', ur'Ι', 1],
    ['replace', ur'li1', ur'ιΙ', 1],
    ['replace', ur'M', ur'Μ', 1],
    ['replace', ur'N', ur'Ν', 1],
    ['replace', ur'Pp', ur'Ρρ', 1],
    ['replace', ur'ϲϹ', ur'σςΣ', 1],#for lunate fonts
    ['replace', ur'c', ur'σς', 1],#for lunate fonts
    ['replace', ur'T', ur'Ττ', 1],
    ['replace', ur'Τ', ur'τ', 1],
    ['replace', ur'Uu', ur'υ', 1],
    ['replace', ur'Y', ur'Υ', 1],
    ['replace', ur'E', ur'Εε', 1],
    ['replace', ur'Z', ur'Ζ', 1],
    ['replace', ur'K', ur'κΚ', 1],
    ['replace', ur'a', ur'α', 1],
    ['replace', ur'ΛΑ', ur'ΛΑ', 1],
    ['insert', ur'*', ur'/\\()|~', 3],
    ['delete', ur'/\\()|~', ur'*', 3],
    ['replace', ur'()~/\\', ur'()~/\\', 2],
    ['replace', ur'σ', ur'ς', 2],  # for lunate fonts
    ['replace', ur'χΧ', ur'χΧ', 2],
    ['replace', ur'κΚ', ur'κΚ', 2],
    ['replace', ur'ι|', ur'ι|', 2]
]

debug = False

"""
A generator function for chopping up a given list into chunks of
length n.
"""
def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]


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
        if (char_num_in_word_one > (len(wordFrom) - 1)):
            char_in_word_one = ''
        else:
            char_in_word_one = wordFrom[char_num_in_word_one]
        if (char_num_in_word_two > (len(wordTo) - 1)):
            char_in_word_two = ''
        else:
            char_in_word_two = wordTo[char_num_in_word_two]
        if (debug):
            print '\t', command
            if char_in_word_one:
                print '\t', unicodedata.name(char_in_word_one)
            else:
                print '\tx'
            if char_in_word_two:
                print '\t', unicodedata.name(char_in_word_two)
            else:
                print '\tx'
        if (command == 'replace'):
            edit_weight = 10
        elif (command == 'delete'):
            edit_weight = 15
        elif (command == 'insert'):
            edit_weight = 18
        else:
            raise ValueError('unknown Levenshtein edit operation: ' + command)
        for weight_rule in weight_rules:
            if (weight_rule[0] == command) and (weight_rule[1] == '*' or char_in_word_one in weight_rule[1]) and (weight_rule[2] == '*' or char_in_word_two in weight_rule[2]):
                if (debug):
                    print '\t weight rule applied:'
                    print '\t', weight_rule
                edit_weight = weight_rule[3]
                break
        if (debug):
            print '\tweight: ', edit_weight
        cumulative_weight += edit_weight
    return cumulative_weight


def Dehyphenate(lines):
    from greek_tools import split_text_token
    import string
    import re
    regex = re.compile(
        '[%s]' % re.escape(string.punctuation + u'〉〈“‘†”—·' + u'0123456789'))
    import nltk
    from nltk.tokenize import RegexpTokenizer
    n = 0
    tokenizer = RegexpTokenizer('[)(·;><.,\s]+', gaps=True)
    # lines = raw.split("\n")
    text_array = []
#        print "lines: ", len(lines)
    for line in lines:
  #              print n, line.encode('utf-8')
        line_tokens = tokenizer.tokenize(line)
#		line_tokens = [regex.sub('',tok) for tok in line_tokens]
#                for token in line_tokens:
#                       print token.encode('utf-8'), " | "
        n = n + 1
        text_array.append(line_tokens)
 #       print "Done printing lines"
    # now try to match hyphenated lines with their
    # correpsonding beginning lines
    n = 0
    for line in text_array[:-2]:
   #             print line
        try:
            # print "last token: ", line[-1].encode('utf-8')
            if line[-1][-1] == '-':
                next_non_empty_line = n + 1
                while (len(text_array[next_non_empty_line]) < 1):
                    next_non_empty_line += 1
     #                           print "line is ", n, "next non empty is: ", next_non_empty_line
      # print "it looks like ",text_array[next_non_empty_line], " and has
      # size", len(text_array[next_non_empty_line])
                line[-1] = line[-1][:-1] + text_array[next_non_empty_line][0]
                text_array[
                    next_non_empty_line] = text_array[next_non_empty_line][1:]
                # print "\tadded to form ",line[-1].encode('utf-8')
        except IndexError:
            pass
        n = n + 1
    # now flatten the 2d array
    tokens = [item for sublist in text_array for item in sublist]
    # now remove extraneous punctuation
    tokens = [split_text_token(tok)[1] for tok in tokens]
    # now remove tokens that are not Greek
#        print "printing tokens"
#        for token in tokens:
#                for word in tokens:
#                        print word.encode('utf-8')
    return tokens


def spellcheck_urls(dict_file, urls, output_file_name, max_weight=10, debug=False):
    from urllib import urlopen
    import nltk
    from nltk.tokenize import RegexpTokenizer
    from itertools import repeat
    from multiprocessing import Pool
    import codecs
    all_tokens = []
    output_file= codecs.open(output_file_name, 'w', 'utf-8')
    #print "numbre of urls: ", len(urls)
    for url in urls:
        raw = urlopen(url).read().decode('utf-8')
        n = 0
        lines = raw.split("\n")
        if debug:
            for line in lines:
                print line

        tokens  =  Dehyphenate(lines)
        if debug:
            for token in tokens:
                print token
        all_tokens = all_tokens + delete_non_greek_tokens(tokens)
    if debug:
        for token in all_tokens:
            print token
    vocab = sorted(set(all_tokens))
    # print "vocab of ", len(vocab), " words"
    vocab = [word for word in vocab if not is_uc_word(word)]
    # print "non-capital words: ", len(vocab)
    print "making dicts"
    word_dicts = makeDict(dict_file)
    vocab_chunks = list(chunks(vocab, len(vocab) / 19))
    print "vocab is ", len(vocab)
    processed_vocab_chunks = zip(vocab_chunks, repeat(word_dicts), repeat(max_weight))
    print "there are ", len(processed_vocab_chunks), "chunks"
   
    # print "dictionary of ", len(dict_words), "words"
    # vocab = [preprocess_word(a_word) for a_word in vocab]
    # why doesn't this trimm all the ones that pass spellcheck?
    # vocab = sorted(set(vocab).difference(set(dict_words)))
    # print "vocab trimmed of dictionary words to ", len(vocab)
    p = Pool(processes=20)
    output = p.map(process_vocab,processed_vocab_chunks)
    for output_chunk in output:
        output_file.write(output_chunk)
##    for chunk in processed_vocab_chunks:
##        print "doing chunk "
##        process_vocab(chunk)

def process_vocab((vocab,word_dicts, max_weight)):
    (dict_words, words_clean, words_freq) = word_dicts
    output_string = ''
    for wordIn in vocab:
        wordIn = preprocess_word(wordIn)
        output_words = getCloseWords(
            wordIn, word_dicts, teubner_serif_weights, threshold=5)
        # If the word doesn't have an exact match, and it is capitalized, then redo with
        # a uncapitalized version
        isCapitalized = False
        hasBeenLowered = False
        if debug:
            print
            print wordIn.encode('utf-8')
        if wordIn.capitalize() == wordIn:
            if debug:
                print wordIn.encode('utf-8'), "is capitalized"
            isCapitalized = True
        min_weight = max_weight + 1
        for output_word in output_words:
            if output_word[3] < min_weight:
                min_weight = output_word[3]
        if debug:
            print "minweight is ", min_weight
        if isCapitalized and (len(output_words) == 0 or min_weight > max_weight):
            if debug:
                for word, lev_distance, n, w, junk1, junk2 in output_words[:8]:
                    print word, words_clean[word].encode('utf-8'), w, lev_distance, words_freq[word]
                print "not found directly, so using", wordIn.lower().encode('utf-8')
            output_words = getCloseWords(wordIn.lower(
            ), word_dicts, teubner_serif_weights, threshold=5)
            hasBeenLowered = True
        # print
        # print wordIn, ":"
        # If the input word is in the dictionary
        if len(output_words) > 0 and output_words[0][1] == 0:
            if debug:
                print "*"
        else:
            if len(output_words) > 0 and output_words[0][3] < max_weight:
                best_result_word = words_clean[output_words[0][0]]
                if (hasBeenLowered):
                    best_result_word = best_result_word.capitalize()
                if not best_result_word == wordIn:
                    output_string += wordIn + "," + best_result_word + '\n'
                # dump(wordIn)
                # print
                # dump(best_result_word)
            for word, lev_distance, n, w, junk1, junk2 in output_words[:8]:
                if (hasBeenLowered):
                    word_to_print = word.capitalize()
                else:
                    word_to_print = word
                if debug:
                    print word_to_print, words_clean[word].encode('utf-8'), w, lev_distance, words_freq[word]
            #		dump(word_to_print)
            #		print
            #		dump(words_clean[word])
                # dump(word)
                if (lev_distance == 0):
                    break
    return output_string

def makeDict(fileName):
    words_transformed = []
    words_clean = {}
    words_freq = {}
    n = 0
    mine = codecs.open(fileName, 'r', 'utf-8')
    for line in mine:
        # wordsInLine = line.split()
        # print len(wordsInLine)
        # for word in wordsInLine:
        (word, freq) = line.split(',')
        # print len(wordsInLine)
        # for word in wordsInLine:
        freq = int(freq.rstrip('\r\n'))
        word = preprocess_word(word)
        thisWord = leven.transIn(word)
        words_transformed.append(thisWord)
        words_clean[thisWord] = word
        words_freq[thisWord] = freq
    # print "dictionary: ",len(words_transformed), " words."
    # for word in words_transformed:
    #	dump(word)
    #	print
    #	dump(words_clean[word])
    #	print
    #	print
    return (words_transformed, words_clean, words_freq)


def preprocess_word(word):
    # ensures that word is in Python's NFD, and checks for bogus circumflexes
    # that don't compose properly
    word = word.replace(' ', '')
    import unicodedata
    circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
    other_circumflex = unicode(u"\N{COMBINING CIRCUMFLEX ACCENT}")
    greek_koronis = unicode(u"\N{GREEK KORONIS}")
    apostrophe = unicode(u"\N{APOSTROPHE}")
    word = word.replace(other_circumflex, circumflex)
    word = word.replace(greek_koronis, apostrophe)
    word = unicodedata.normalize('NFD', word)
    return word


def unicode_test(word):
    import unicodedata
    print
    print
    circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
    other_circumflex = unicode(u"\N{COMBINING CIRCUMFLEX ACCENT}")
    word = word.replace(other_circumflex, circumflex)
    print "*** ", word, ": "
    print "Input: "
    dump(word)
    nfd = unicodedata.normalize('NFD', word)
    if not word == nfd:
        print "The decomposed verison is NOT the same: ",
        print nfd
        dump(nfd)
    else:
        print "(NFD is the same)"
    try:
        cfd = unicodedata.normalize('NFC', word)
    except Error as foo:
        print foo

    print "CFD: ", cfd
    dump(cfd)


def getCloseWords(wordIn, word_dicts, rules, threshold=2, fast=True):
    import Levenshtein
    # out = difflib.get_close_matches('ἐστιν',words)
    (dict_words, words_clean, words_freq) = word_dicts
    # print "word in:"
    # print dump(wordIn)
    # wordIn = preprocess_word(wordIn)
    # print "word in pp:"
    # print dump(wordIn)
    wordInTrans = leven.transIn(wordIn)
    # print
    # print wordInTrans.encode('utf-8'), "(", wordIn.encode('utf-8'),")"
    # dump(wordInTrans)
    output_words = []
    n = 0
    # print "Now comparing to..."
    for word in dict_words:
        # print u"*****" + words_clean[n]
        # print "word into comparison:"
        # print dump(word)
        lev_distance = Levenshtein.distance(
            wordInTrans, word)  # difflib.SequenceMatcher(None, word, wordInTrans).ratio()
        # print "distance: ",
        # print ratio
        if lev_distance <= threshold:
            edits = Levenshtein.editops(wordInTrans, word)
            w = weight_for_leven_edits(wordInTrans, word, edits, rules)
            output_words.append(
                (word, lev_distance, len(edits), w, 'xxx', 'yyy'))
            if (lev_distance == 0) and (fast == True):
                # In the case of an exact match, cut the search short
                # We might have got some close matches ahead of time, so this
                # will not create a complete list
                output_words = sorted(
                    output_words, key=lambda word: int(words_freq[word[0]]))
                return sorted(output_words, key=lambda word: int(word[3]))
        n = n + 1
    return sorted(output_words, key=lambda word: word[3])

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   # main()
    import sys
    spellcheck_urls(sys.argv[1], sys.argv[2:-1], sys.argv[-1], debug=False)

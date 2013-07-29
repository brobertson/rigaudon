#!/usr/bin/python
# vim: set fileencoding=UTF-8 :
from gamera.core import init_gamera
init_gamera()
import lxml
from lxml import etree
import sys
from operator import itemgetter, attrgetter
DEBUG=False

class hocrWord():
    """associates word text with bbox"""


class hocrLine():
    """Associates lines, words with their text and bboxes"""

    """Associates hocr lines with text origin"""



def parse_bbox(stringIn):
    from gamera.core import Rect
    from gamera.core import Point
    dimensions = stringIn.split()
    if not dimensions[0] == 'bbox' or not len(dimensions) == 5:
        raise ValueError('bounding box not in proper format: "%s"'%dimensions)
    a_rect = Rect(Point(int(dimensions[1]),int(dimensions[2])),Point(int(dimensions[3]),int(dimensions[4])))
    return (a_rect)#dimensions[1:])


def get_hocr_lines_for_tree(treeIn):

    root = treeIn.getroot()
    hocr_line_elements = treeIn.xpath("//html:span[@class='ocr_line'] | //span[@class='ocr_line']",namespaces={'html':"http://www.w3.org/1999/xhtml"})
    line_counter = 0
    lines_out = []
    all_words = []
    for hocr_line_element in hocr_line_elements:
        #print "line: ", line_counter, parse_bbox(hocr_line_element.get('title'))
        line_counter += 1
        words = hocr_line_element.xpath(".//html:span[@class='ocr_word'] | .//span[@class='ocr_word'] ",namespaces={'html':"http://www.w3.org/1999/xhtml"})
        word_counter = 0
        words_out = []
        for word in words:
           # print "\tword: ", word_counter, word.text, parse_bbox(word.get('title'))
            aWord = hocrWord()
            aWord.text = ""
            if word.text:
               aWord.text += word.text
            #get rid of any inner elements, and just keep their text values
            for element in word.iterchildren():
              if element.text:
                 aWord.text += element.text
              word.remove(element)
            #set the contents of the xml element to the stripped text
            word.text = aWord.text
            aWord.bbox = parse_bbox(word.get('title'))
            aWord.element = word
            words_out.append(aWord)
        aLine = hocrLine()
        all_words = all_words + words_out
        aLine.words = words_out
        aLine.element = hocr_line_element
        aLine.bbox = parse_bbox(hocr_line_element.get('title'))
        lines_out.append(aLine)
    return lines_out, all_words


def close_enough(bbox1, bbox2):
    total_circum1 = (bbox1.lr_x - bbox1.ul_x) * 2 + (bbox1.lr_y - bbox1.ul_y) * 2
    total_circum2 =  (bbox1.lr_x - bbox1.ul_x) * 2 + (bbox1.lr_y - bbox1.ul_y) * 2
    fudge = (total_circum1 + total_circum2) * 0.1
    if DEBUG: print 'fudge', fudge
    total_diff = (abs(bbox1.lr_x - bbox2.lr_x) + abs(bbox1.lr_y - bbox2.lr_y) + abs(bbox1.ul_x  - bbox2.ul_x) + abs(bbox1.ul_y - bbox2.ul_y))
    if DEBUG: print 'total_diff', total_diff
    if total_diff < fudge:
        return True
    else:
        return False


def sort_words_bbox(words):
    words.sort( key=attrgetter('bbox.lr_y'))
    words.sort( key=attrgetter('bbox.lr_x'))
    words.sort(key=attrgetter('text'))
    return words


def score_word(word):
    IN_DICT_SCORE = 1000
    IN_DICT_LOWER_SCORE = 100
    CAMEL_CASE_SCORE = 1
    ALL_CAPS_SCORE = 10
    score_total = 0
    if in_dict(dictionary, word):
        score_total = score_total + IN_DICT_SCORE
    elif in_dict_lower(dictionary, word):
            score_total = score_total + IN_DICT_LOWER_SCORE
    if score_total > 0:
        if word.istitle():
            score_total = score_total + CAMEL_CASE_SCORE
        elif word.isupper():
            score_total = score_total + ALL_CAPS_SCORE
    return score_total


dictionary = []
import codecs
import os
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
dictionaryFile = codecs.open(sys.argv[1],'r',encoding='UTF-8')
for line in dictionaryFile:
    (word,freq) = line.split(',')
    dictionary.append(word)
dictionary = set(dictionary)
fileIn1 = open(sys.argv[2],'r')
tree1 = etree.parse(fileIn1)
lines_1, words_1 = get_hocr_lines_for_tree(tree1)
sort_words_bbox(words_1)
if DEBUG:
    print "words_1:"
    for word in words_1:
        print word.text, word.bbox

other_words = []
for fileInName in sys.argv[3:-2]:
    try:
        print "processing:", fileInName
        fileIn2 = open(fileInName,'r')
        tree2 = etree.parse(fileIn2)
        lines_2, words_2 = get_hocr_lines_for_tree(tree2)
        if DEBUG:
            for word in words_2:
                print word.text, word.bbox
        other_words = other_words + words_2
    except Exception as e:
        print e

sort_words_bbox(other_words)
positional_lists = []
positional_list = []
x = 0

#Make a list of positional_lists, that is alternatives for a give position, skipping duplicate position-words
while x < len(other_words):
    if DEBUG: print other_words[x].text, other_words[x].bbox
    try:
        if len(positional_list) == 0:
            positional_list.append(other_words[x])
        else:
            if close_enough(other_words[x -1].bbox,other_words[x].bbox):
                if DEBUG: print "same position as previous"
                #skip if the text is the same, so that we just get unique texts for this position
                if not other_words[x-1].text == other_words[x].text:
                    if DEBUG: print "to be added"
                    positional_list.append(other_words[x])
            else:
                if not x == 0:
                    positional_lists.append(positional_list)
                    positional_list = []
    except IndexError:
        pass
    x = x + 1

# we now have a list of list of unique words for each position
# let's select from each the first one that passes spellcheck
from greek_tools import in_dict, in_dict_lower, is_greek_string, is_number, split_text_token
replacement_words = []

#make a 'replacement_words' list with all of the best, non-zero-scoring
#suggestions for each place
for positional_list in positional_lists:
    for word in positional_list:
        word.score = score_word(word.text)
    positional_list.sort(key=attrgetter('score'), reverse=True)
    if positional_list[0].score > 0:
        replacement_words.append(positional_list[0])

#now replace the originals
for word in words_1:
    for replacement_word in replacement_words:
        word.score = score_word(word.text)
        if close_enough(word.bbox,replacement_word.bbox) and (word.score < replacement_word.score):
            if DEBUG: print "replacing", word.text, word.score, "with", replacement_word.text, replacement_word.score
            word.element.text = replacement_word.text


if DEBUG:
    print "replacment words:"
    for word in replacement_words:
        print word.text


    for positional_list in positional_lists:
        print "##"
        for word in positional_list:
            print word.bbox, word.text



out_file = open(sys.argv[-1],'w')
out_file.write(etree.tostring(tree1.getroot(), xml_declaration=True))
out_file.close()


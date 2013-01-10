#!/usr/bin/python
from gamera.core import init_gamera
init_gamera()
import lxml
from lxml import etree
import sys

class hocrWord():
    """associates word text with bbox"""
    

class hocrLine():
    """Associates lines, words with their text and bboxes"""

class hocrDoc():
    """Associates hocr lines with text origin"""

def parse_bbox(stringIn):
    from gamera.core import Rect
    from gamera.core import Point
    dimensions = stringIn.split()
    if not dimensions[0] == 'bbox' or not len(dimensions) == 5:
        raise ValueError('bounding box not in proper format: "%s"'%dimensions)
    a_rect = Rect(Point(int(dimensions[1]),int(dimensions[2])),Point(int(dimensions[3]),int(dimensions[4])))
    return (a_rect)#dimensions[1:])

def rect_offset(rect1, rect2):
    from gamera.core import Rect
    #from gamera.core import Distance
    offset_x = rect1.distance_cx(rect2)
    offset_y = rect1.distance_cy(rect2)
    return (offset_x,offset_y)


def get_hocr_lines_for_file(fileIn):
    tree = etree.parse(fileIn)
    root = tree.getroot()
    hocr_line_elements = tree.xpath("//html:span[@class='ocr_line'] | //span[@class='ocr_line']",namespaces={'html':"http://www.w3.org/1999/xhtml"})
    line_counter = 0
    lines_out = []
    for hocr_line_element in hocr_line_elements:
        #print "line: ", line_counter, parse_bbox(hocr_line_element.get('title'))
        line_counter += 1
        words = hocr_line_element.xpath(".//html:span[@class='ocr_word'] | .//span[@class='ocr_word'] ",namespaces={'html':"http://www.w3.org/1999/xhtml"})
        word_counter = 0
        words_out = []
        for word in words:        
           # print "\tword: ", word_counter, word.text, parse_bbox(word.get('title'))
            aWord = hocrWord()
            aWord.text = word.text
            aWord.bbox = parse_bbox(word.get('title'))
            aWord.element = word
            words_out.append(aWord)
        aLine = hocrLine()
        aLine.words = words_out
        aLine.element = hocr_line_element
        aLine.bbox = parse_bbox(hocr_line_element.get('title'))
        lines_out.append(aLine)      
    return lines_out

def dump_lines(lines_out):
    for line_out in lines_out:
        print 'LINE', line_out.element
        for word_out in line_out.words:
            print '\t', word_out.text, word_out.bbox,  word_out.element

def compare_hocr_lines(lines1, lines2, x_tolerance, y_tolerance):
    if not len(lines1) == len(lines2):
        raise ValueError("hocr lines are not equal in number")
    pairs = zip(lines1, lines2)
    for pair in pairs:
        (offset_x, offset_y) = rect_offset(pair[0].bbox, pair[1].bbox)
        if offset_y > y_tolerance:
            raise ValueError('hocr lines do not align vertically within tolerance %s'%y_tolerance)
        else:
            print "hocr files pass alignment of ", len(lines1), " lines with tolerance of ", y_tolerance
   # print "comparing words"
    for pair in pairs:
        print "new line"
        words_1 = pair[0].words
        words_2 = pair[1].words
        line_matches = []
        word_1_matches = []
        word_2_matches = []
        for word in words_1:
           # print
         #   print '\t', word.bbox, word.text
            for word_2 in words_2:
                (offset_x, offset_y) = rect_offset(word.bbox, word_2.bbox)
                if offset_x < x_tolerance:
                    word_1_matches.append(word)
                    word_2_matches.append(word_2)
                    line_matches.append(([word],[word_2]))
                   # print "\tI think is equal to:"
                   # print '\t', word_2.bbox, word_2.text
        #we've done the simple ones, now for the hard ones
        unmatched_words_1 = [x for x in words_1 if x not in word_1_matches]
        unmatched_words_2 = [x for x in words_2 if x not in word_2_matches]
        current_word_1 = 0
        current_word_2 = 0
        left_match = []
        right_match = []

        while current_word_1 < len(unmatched_words_1):
            while current_word_2 < len(unmatched_words_2):
                left_difference = unmatched_words_1[current_word_1].bbox.ul_x - unmatched_words_2[current_word_2].bbox.ul_x
                print "left difference: ", left_difference
                if abs(left_difference) < x_tolerance:
                    left_match.append(unmatched_words_1[current_word_1])
                    right_match.append(unmatched_words_2[current_word_2])
                    right_difference = unmatched_words_1[current_word_1].bbox.lr_x - unmatched_words_2[current_word_2].bbox.lr_x
                    print "right difference: ", right_difference
                    while abs(right_difference) > x_tolerance and current_word_2 < len(unmatched_words_2)-1 and current_word_1 < len(unmatched_words_1)-1:
                        print "did loop"
                        if right_difference > 0 and ((current_word_2 < len(unmatched_words_2)) or (unmatched_words_2[current_word_2 + 1].bbox.ul_x < unmatched_words_1[current_word_1].bbox.lr.x)):
                            #ensure that the next word of the second document is within the box of the first
                            current_word_2 += 1
                            right_match.append(unmatched_words_2[current_word_2])
                        elif right_difference < 0 and unmatched_words_1[current_word_1 + 1].bbox.ul_x < unmatched_words_2[current_word_2].bbox.lr.x:
                            #ensured that the next word from the first document is within the box of the second
                            current_word_1 += 1
                            left_match.append(unmatched_words_1[current_word_1])
                        else:#means that one of the above are bigger than they ought to be, so we'll just append what we have
                            break
                        right_difference = unmatched_words_1[current_word_1].bbox.lr_x - unmatched_words_2[current_word_2].bbox.lr_x
                    line_matches.append((left_match,right_match))     
                current_word_2 += 1
            current_word_1 += 1
        for match in line_matches:
            (left_match, right_match) = match
            for word in left_match:
                print word.text,
            print "\t\t\t\t",
            for word in right_match:
                print  word.text, " ",
            print
    return True



fileIn1 = open(sys.argv[1],'r')
fileIn2 = open(sys.argv[2],'r')
lines_out_1 = get_hocr_lines_for_file(fileIn1)
lines_out_2 = get_hocr_lines_for_file(fileIn2)
#dump_lines(lines_out_1)
#print "new"
#dump_lines(lines_out_2)

#print "comparing..."
#print "1 has : ",len(lines_out_1), "lines"
#print "2 has : ",len(lines_out_2), "lines"



compare_hocr_lines(lines_out_1, lines_out_2,2,2)

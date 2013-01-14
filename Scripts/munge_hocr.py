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


def get_hocr_lines_for_tree(treeIn):
   
    root = treeIn.getroot()
    hocr_line_elements = treeIn.xpath("//html:span[@class='ocr_line'] | //span[@class='ocr_line']",namespaces={'html':"http://www.w3.org/1999/xhtml"})
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
        print 'LINE', line_out.bbox 
        #for word_out in line_out.words:
        #    print '\t', word_out.text, word_out.bbox,  word_out.element

def sort_lines_top_bottom_left_right(lines):
    lines.sort(key=lambda line: line.bbox.lr_y)
    lines.sort(key=lambda line: line.bbox.ul_x)
    return lines

def dump_words(words):
    for word in words:
        print word.text, word.bbox

def dump_words_alone(words):
    for word in words:
        print word.text,
    print
    
def total_x_offset(rect1, rect2):
    print "doing x offset"
    print rect1, rect2
    difference = abs(rect1.ul_x - rect2.ul_x) + abs(rect1.lr_x - rect2.lr_x)
    print difference
    return difference

def distance_between_uls(bbox1, bbox2):
    import math
    return math.sqrt((bbox1.ul_x - bbox2.ul_x)**2 + (bbox1.ul_y - bbox2.ul_y)**2)

def compare_hocr_lines(lines1, lines2, x_tolerance, y_tolerance):
    lines1 = sort_lines_top_bottom_left_right(lines1)
    lines2 = sort_lines_top_bottom_left_right(lines2)
    lines2_copy = lines2[:]
    print "at start lines2 is: ", len(lines2)
    line_pairs = []
    if not len(lines1) == len(lines2):
        raise ValueError("hocr lines are not equal in number")
    for line1 in lines1:
        #print "doing line1 ", line1.bbox
        already_matched = False
        min_distance_candidate = lines2_copy[0]
        #print "initial mdc: ", min_distance_candidate.bbox
        for line2 in lines2_copy[1:]:
            #print "\t cp. line2: ", line2.bbox
            l2d = distance_between_uls(line1.bbox, line2.bbox)#line1.bbox.distance_bb(line2.bbox)
            mdcd = distance_between_uls(line1.bbox, min_distance_candidate.bbox)#line1.bbox.distance_bb(min_distance_candidate.bbox)
            #print "\t mdcd: ", mdcd
            #print "\t distance: ", l2d
            #if distance_between_uls(line1.bbox, line2.bbox) < distance_between_uls(line1.bbox, min_distance_candidate.bbox):#
            if l2d < mdcd:
                #print "\t\tmade line2 mdc"
                min_distance_candidate = line2
        line_pairs.append((line1,min_distance_candidate))
        lines2_copy.remove(min_distance_candidate)
    if not len(line_pairs) == len(lines1):
        raise ValueError("not all lines were matched")
    print "at end lines2 is ", len(lines2)
    max_x_offset = 0
    max_y_offset = 0
    for line_pair in line_pairs:
        print "new line"
        words_1 = line_pair[0].words
        words_2 = line_pair[1].words
        line_matches = []
        word_1_matches = []
        word_2_matches = []
        unmatched_words_1 = line_pair[0].words
        unmatched_words_2 = line_pair[1].words
        current_word_1 = -1
        current_word_2 = 0
        left_match = []
        right_match = []
        
        while current_word_1 < len(unmatched_words_1):
            current_word_1 += 1
            while current_word_2 < len(unmatched_words_2) and current_word_1 < len(unmatched_words_1):
                left_difference = unmatched_words_1[current_word_1].bbox.ul_x - unmatched_words_2[current_word_2].bbox.ul_x
                #print "cw1: ", current_word_1
                #print "cw2: ", current_word_2
                #print "left difference: ", left_difference
                right_difference = unmatched_words_1[current_word_1].bbox.lr_x - unmatched_words_2[current_word_2].bbox.lr_x
                        
                if abs(left_difference) < x_tolerance:
                    left_match.append(unmatched_words_1[current_word_1])
                    right_match.append(unmatched_words_2[current_word_2])
                    while abs(right_difference) > x_tolerance and (current_word_2 < len(unmatched_words_2)-1 or current_word_1 < len(unmatched_words_1)-1):
                        #print "did loop"
                        if right_difference > 0 and ((current_word_2 < len(unmatched_words_2)) or (unmatched_words_2[current_word_2 + 1].bbox.ul_x < unmatched_words_1[current_word_1].bbox.lr.x)):
                            #ensure that the next word of the second document is within the box of the first
                            #print "adding one from right"
                            current_word_2 += 1
                            right_match.append(unmatched_words_2[current_word_2])
                        elif right_difference < 0 and ((current_word_1 < len(unmatched_words_1) or unmatched_words_1[current_word_1 + 1].bbox.ul_x < unmatched_words_2[current_word_2].bbox.lr.x)):
                            #ensured that the next word from the first document is within the box of the second
                            #print"adding one from left"
                            current_word_1 += 1
                            left_match.append(unmatched_words_1[current_word_1])
                        else:#means that one of the above are bigger than they ought to be, so we'll just append what we have
                            #print "breaking"
                            break
                        right_difference = unmatched_words_1[current_word_1].bbox.lr_x - unmatched_words_2[current_word_2].bbox.lr_x
                        #print "right difference: ", right_difference
                    #print "appending values"   
                    line_matches.append((left_match,right_match))
                    left_match=[]
                    right_match= []
                current_word_2 += 1
            current_word_2 = 0
        for match in line_matches:
            (left_match, right_match) = match
            for word in left_match:
                print word.text, word.element,
            print "\t\t\t\t",
            for word in right_match:
                print  word.text, word.element
            print
            line_pair[1].line_matches = line_matches
    print "lines2 on return: ", len(lines2)
    return lines2

def grecify_left(right_lines):
    import unicodedata
    print "doing grecify"
    print 'linematches length: ', len(right_lines)
    from greek_tools import is_greek_string
    
    for lines in right_lines:
        for match in lines.line_matches:
            (left_match, right_match) = match
            test_word = ""
            for word in right_match:
               test_word += word.text
            print "test_word: ", test_word
            if is_greek_string(test_word):
                print "replacing left"
                left_match[0].element.text = unicodedata.normalize('NFD',test_word)
		left_match[0].element.set("lang","grc")
		left_match[0].element.set("{http://www.w3.org/XML/1998/namespace}lang","grc")
    

fileIn1 = open(sys.argv[1],'r')
tree1 = etree.parse(fileIn1)
fileIn2 = open(sys.argv[2],'r')
tree2 = etree.parse(fileIn2)
lines_1 = get_hocr_lines_for_tree(tree1)
lines_2 = get_hocr_lines_for_tree(tree2)

my_line_matches = compare_hocr_lines(lines_1, lines_2,15,15)

grecify_left(my_line_matches)

out_file = open(sys.argv[3],'w')
out_file.write(etree.tostring(tree1.getroot(), xml_declaration=True))
out_file.close()



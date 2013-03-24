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


def sort_lines_left_right_top_bottom(lines):
    lines.sort(key=lambda line: line.bbox.ul_x)
    lines.sort(key=lambda line: line.bbox.lr_y)
    return lines

def delete_etree_element(bad_element):
    try:
        bad_element.getparent().remove(bad_element)
    except AttributeError as e:
        #sometimes we get AttributeError: 'NoneType' object has no attribute 'remove'
        #that's strange. TODO
        pass
    
def generate_bbox_title_hocr_text(line):
    x_start = str(line.bbox.ul_x)
    x_end = str(line.bbox.lr_x)
    y_start = str(line.bbox.ul_y)
    y_end = str(line.bbox.lr_y)
    out = "bbox " + x_start + " " + y_start + " " + x_end + " " + y_end
    return out

def fix_overlapping_hocr_lines(lines1):
      lines1 = sort_lines_left_right_top_bottom(lines1)
      for line in lines1:
          print line.bbox
          line.element.attrib["title"] = generate_bbox_title_hocr_text(line)
      counter = 0
      for line in lines1:
          for line_beneith in lines1[counter+1:]:
              if line.bbox.intersects(line_beneith.bbox):
                  if line.bbox.lr_y > line_beneith.bbox.ul_y:
                      line.bbox.lr_y = line_beneith.bbox.ul_y
                      line.bbox.ll_y = line_beneith.bbox.ul_y
                      if line.bbox.height > 20:
                          line.element.attrib["title"] = generate_bbox_title_hocr_text(line)
                      else:
                          print "deleting small line element: ", line.bbox
                          delete_etree_element(line.element)
                        
          counter+= 1


fileIn1 = open(sys.argv[1],'r')
tree1 = etree.parse(fileIn1)
lines_1 = get_hocr_lines_for_tree(tree1)

fix_overlapping_hocr_lines(lines_1)

out_file = open(sys.argv[2],'w')
out_file.write(etree.tostring(tree1.getroot(), xml_declaration=True))
out_file.close()



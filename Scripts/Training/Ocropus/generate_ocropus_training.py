from HTMLParser import HTMLParser
from gamera.core import *

init_gamera()
from gamera.plugin import *
class SpanLister(HTMLParser):
    def __init__(self, id_string):
	HTMLParser.__init__(self)
	self.id_string = id_string



    def reset(self):
            HTMLParser.reset(self)
            self.spans = []
    def handle_starttag(self, tag, attrs):
            foo = [v for k, v in attrs if k=='class']
            bar = [j for i, j in attrs if i=='title']
            if foo:
		if foo[0] == self.id_string:
                	print foo[0]
			#print self.get_starttag_text()
                	self.spans.extend(bar)
def drawParser(parser,color,image,image_name, invert = False):
	import os
	file_number = 0
	image_basename = os.path.splitext(image_name)[0]
	print "another len:", len(parser.spans)
	for span in parser.spans:
	    print 'span', span
	    boxes =  span.split(';')[0].split()
	    print 'boxes', boxes
	    y1 = int(boxes[2]) - 1
	    y2 = int(boxes[4]) -1
	    x1 = int(boxes[1]) - 1
	    x2 = int(boxes[3])-1
	    #P1 = P2 = None
	    if invert:
	        y1 = image.nrows - y1
	        y2 = image.nrows - y2
	        P1 = (x1, y2)
	        P2 = (x2, y1)
	    else:
	        P1 = (x1, y1)
	        P2 = (x2, y2)
	    print "P1", P1
	    print "P2", P2
	    subimg = SubImage(image, P1, P2)
	    subimg.save_PNG(image_basename + '_' + str(file_number) + '.bin.png')
	    file_number = file_number +1
	    print 'now on file num', file_number


lineParser = SpanLister('ocr_line')
#wordParser  = SpanLister('ocr_word')
#wordXParser = SpanLister('ocrx_word')
image_name = sys.argv[1]
hocr_name = sys.argv[2]
#dirName = name[:len(name)-5]
#print dirName
image = load_image(image_name)
image = image.to_rgb()
lineParser.feed(open(hocr_name).read())
print "spans", len(lineParser.spans)
#wordParser.feed(open(hocr_name).read())
#wordXParser.feed(open(hocr_name).read())
print "about to do drawParser"
drawParser(lineParser,RGBPixel(255,0,255),image,image_name )
import os
base_filename = os.path.splitext(image_name)[0]
#we have .bin form, so we need to split again
#base_filename = os.path.splitext(base_filename)[0]
text_filename = base_filename + '.gt.txt'
text_file = open(text_filename,'r')
text_file.readline()
file_number = 0
for line in text_file:
	out_file = open(base_filename + '_' + str(file_number) + '.gt.txt','w')
	out_file.write(line)
	out_file.close()
	file_number += 1

#drawParser(wordParser,RGBPixel(0,255,255),image)
#drawParser(wordXParser,RGBPixel(255,0,255),image)

#save the image
#print "image out: ", sys.argv[3]
#image.save_PNG(sys.argv[3])

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
                	self.spans.extend(bar)

def generateCCsFromHocr(parser,image):
	from gamera.core import Point
	ccs_lines = []
	label  = 1
	for span in parser.spans: 
		boxes =  span.split(';')[0].split()
		point1 = Point(int(boxes[1]),int(boxes[2]))
		point2 = Point(int(boxes[3]),int(boxes[4]))
		try:
			ccs_lines.append(Cc(image, label, point1, point2))
		except RuntimeError as e:
		#TODO we should do something here
		#	print "failed to make Cc from Hocr box: "
		#	print boxes 
			pass
		label = label + 1
	return ccs_lines

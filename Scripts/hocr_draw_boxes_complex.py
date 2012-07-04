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
def drawParser(parser,color,image):
	for span in parser.spans: 
		boxes =  span.split(';')[0].split()
		#draw the word boxes
		image.draw_hollow_rect((int(boxes[1]) -1,int(boxes[2]) -1),(int(boxes[3]) +1 , int(boxes[4]) +1 ), color, 2)
lineParser = SpanLister('ocr_line')
wordParser  = SpanLister('ocr_word')
#wordXParser = SpanLister('ocrx_word')
image_name = sys.argv[1]
hocr_name = sys.argv[2]
#dirName = name[:len(name)-5]
#print dirName
image = load_image(image_name)
image = image.to_rgb()
lineParser.feed(open(hocr_name).read())
wordParser.feed(open(hocr_name).read())
#wordXParser.feed(open(hocr_name).read())
drawParser(lineParser,RGBPixel(255,0,255),image)
drawParser(wordParser,RGBPixel(0,255,255),image)
#drawParser(wordXParser,RGBPixel(255,0,255),image)

#save the image
print "image out: ", sys.argv[3]
image.save_PNG(sys.argv[3])	

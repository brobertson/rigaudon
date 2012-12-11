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
	from gamera.core import Point, Cc, Rect
	extended_segs = []
	for span in parser.spans: 
		boxes =  span.split(';')[0].split()
		point1 = Point(int(boxes[1]),int(boxes[2]))
		point2 = Point(int(boxes[3]),int(boxes[4]))
		try:
			extended_segs.append(Rect(point1, point2))
		except RuntimeError as e:
		#TODO we should do something here
		#	print "failed to make Cc from Hocr box: "
		#	print boxes 
			pass
        page = image.image_copy()
        ccs = page.cc_analysis()
	#The following copied from bbox_merging. Simply making Ccs with
	#the appropriate dimensions does not seem to work, but did in a 
	#previous version...
	#extended_segs are the line bboxes; ccs are the glyphs
	#found by page analysis
	# build new merged CCs
        tmplist = ccs[:]
        dellist = []
        seg_ccs = []
        seg_cc = []
        if(len(extended_segs) > 0):
            label = 1
            for seg in extended_segs:
                label += 1
        #        print "new line!"
                for cc in tmplist:
		    descender = (float(cc.lr_y - seg.lr_y) / float(seg.height))
		    if seg.intersects(cc):
                       downness = cc.lr_y - seg.lr_y 
                       segheight = seg.height
         #              print "desc: " + str(descender) + " downness: " + str(downness) + " segheight: " + str(segheight)
                    if(seg.intersects(cc) and ((cc.lr_y < seg.lr_y) or ((float(cc.height) > float(seg.height)/2.0) and (descender  < 0.2) ))):
		    #for more open texts:
		    #if(seg.intersects(cc) and ((cc.lr_y < seg.lr_y) or (descender < 0.4)) ):
                        # mark original image with segment label
                        image.highlight(cc, label)
                        seg_cc.append(cc)
                        dellist.append(cc)
                if len(seg_cc) == 0:
                    continue
                seg_rect = seg_cc[0].union_rects(seg_cc)
                new_seg = Cc(image, label, seg_rect.ul, seg_rect.lr)
                seg_cc = []
                for item in dellist:
                    tmplist.remove(item)
                dellist = []
                seg_ccs.append(new_seg)

        return seg_ccs

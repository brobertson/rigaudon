import sys
import mahotas as mh
import numpy as np
from pylab import imshow, gray, show
#from os import path
from gamera.plugins import numpy_io
#from gamera.core import *
from gamera.plugins.listutilities import median
from gamera.toolkits.ocr.classes import Page

class ImageSegmentationError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
		
	
class FindAppCrit(Page):
	def page_to_lines(self):
		#this subdivides app. crit. in teubners
		
		#this cuts up app. crit into lines
		#self.ccs_lines = self.img.projection_cutting(Tx=25, Ty=8, noise=3)	
		#self.ccs_lines = self.img.projection_cutting(Tx=2000, Ty=5, noise=15)
		self.ccs_lines = self.img.bbox_merging(Ey=8)#this finds app. crit
		
		#word-by-word body of teubner
		#self.ccs_lines = self.img.bbox_merging(Ex=15,Ey=5)
		#self.ccs_lines = self.img.bbox_mcmillan(None,2,4,20,5)

class AppCrit(Page):
	def page_to_lines(self):
		#this cuts up app. crit into lines
		self.ccs_lines = self.img.projection_cutting(Tx=1700, Ty=1, noise=28)
	
class Body(Page):
	def page_to_lines(self):
		#word-by-word body of teubner
		self.ccs_lines = self.img.bbox_merging(Ex=30,Ey=2)
	
def my_filter(imageIn):
	MAX_CCS = 4000
	count = 0
	image = imageIn
	#imageIn.remove_border()
	ccs = image.cc_analysis()
	print "filter started on",len(ccs) ,"elements..."
	if len(ccs) < 1:
		raise ImageSegmentationError("there are no ccs")
	if len(ccs) > MAX_CCS:
		raise ImageSegmentationError("there are more than " + str(MAX_CCS) + " ccs.")
	median_black_area = median([cc.black_area()[0] for cc in ccs])
	#filter long vertical runs left over from margins
	median_height = median([cc.nrows for cc in ccs])
	for cc in ccs:
		if((cc.nrows / cc.ncols > 6) and (cc.nrows > 1.5 * median_height) ):
			cc.fill_white()
			del cc
			count = count + 1

	for cc in ccs:
		if(cc.black_area()[0] > (median_black_area * 10)):
			cc.fill_white()
			del cc
			count = count + 1
	for cc in ccs:
		if(cc.black_area()[0] < (median_black_area / 10)):
			cc.fill_white()
			del cc
			count = count + 1
	print "filter done.",len(ccs)-count,"elements left."

def show_lines(page):
    """Returns an RGB image with all segmented text lines marked by hollow 
rects. Makes only sense after *page_to_lines* (or *segment*) has 
been called.
"""
    from gamera.toolkits.ocr.ocr_toolkit import show_bboxes
    return show_bboxes(page.img, page.ccs_lines)

def plain(imageIn):
   from gamera.toolkits.ocr.classes import Page
   my_filter(imageIn)
   
   q = FindAppCrit(imageIn)
   q.segment()
   return (show_lines(q))


def filter_and_bbox(imageIn):
   from gamera.toolkits.ocr.classes import Page
   image2 = imageIn.image_copy()
   p = FindAppCrit(imageIn)
   p.segment()
   print "image width: " + str(imageIn.ncols)
   s = sorted(p.ccs_lines, key=lambda cc: cc.offset_y)
   s.reverse()
   x = 0 
   for cc in s:
   	#has to be reasonably wide, and not higher than 2/3 down the page
   	x = x + 1
   	if cc.ncols > 0.6 * imageIn.ncols and cc.offset_y > 0.6 * imageIn.nrows:
   		print "Image rows: " + str(imageIn.nrows)
   		print str(cc.ncols) + "x" + str(cc.offset_y)
   		cc.fill_white()
   		break
   
   im = imageIn.image_copy()
   im.reset_onebit_image()
   p = Body(im)
   p.segment()
   print "x = " + str(x)
   print len(s)
   if x == len(s):
   	#then there wasn't an app. crit found
   	print "no app crit found"
   q = only_app_crit(image2, x)
   return (show_lines(p),q)

def only_app_crit(imageIn, xIn):
   from gamera.toolkits.ocr.classes import Page
   p = FindAppCrit(imageIn)
   p.segment()
   s = sorted(p.ccs_lines, key=lambda cc: cc.offset_y)
   s.reverse()
   x = 0 
   for cc in s:
   	x = x + 1
   	if not (x == xIn):
   		cc.fill_white()
   im = imageIn.image_copy()
   im.reset_onebit_image()
   p = AppCrit(im)
   p.segment()
   return show_lines(p)
   
def my_application():
   from gamera.toolkits.ocr.classes import Page
   # Make the image variable a global variable
   # IF YOU DON'T DO THIS, THE WINDOW WILL DISAPPEAR!
   global image, ots, ots_up, ots_mid, box_image, ots_low
   print sys.argv[-1]
   #image_color = load_image(sys.argv[-1])
   picture = mh.imread(sys.argv[-1], as_grey=True)
   picture = picture.astype(np.uint8)
   # Load the image
   image = numpy_io.from_numpy(picture)#load_image(sys.argv[-1]
   #image = image_color.to_greyscale()
   # Display the image in a window
   #image.simple_sharpen()
   ots = image.otsu_threshold()
   thresh = image.otsu_find_threshold()
   #thresh_low = int(thresh* 1.05)
   thresh_mid = thresh_plus = int(thresh * 1.0)
   ots_mid = image.threshold(thresh_mid)
   my_filter(ots_mid)
   ots_up = ots_mid.image_copy()#image.threshold(thresh_plus)
   #ots_up.remove_border()
   
  # ots_low = image.threshold(thresh_low)
   print "OTSU: " + str(thresh)
   print "OTSU Mid: " + str(thresh_mid)
   print "OTSU * 1.15: " + str(thresh_plus)
   #ots_low = filter_and_bbox(ots_low)
   #ots = filter_and_bbox(ots)
   (ots_up,ots_mid) = filter_and_bbox(ots_up)
   #ots_mid = only_app_crit(ots_mid,x)
   #print "x is " + str(x)
   ots_up.display("OTSU-border")
   ots_mid.display()
   #ots_orig.display()
   #ots_mid = show_lines(p)
   #box_image.display()
   #my_filter(ots_mid)
   #ots_up.display("OTSU+FIL")
   #ots_mid = filter_and_bbox(ots_mid)
   #ots_mid.display("MID")
   #ots.display("OTSU")
   #ots_low.display("OTSU_LOW")
   #image.display()
# Import the Gamera core and initialize it
from gamera.core import *
init_gamera()

# Import the Gamera GUI and start it
from gamera.gui import gui
gui.run(my_application)

# The GUI thread will automatically stop when all windows have
# been closed.
print "Goodbye!"

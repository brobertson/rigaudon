import sys
import mahotas as mh
import numpy as np
from pylab import imshow, gray, show
#from os import path
from gamera.plugins import numpy_io
#from gamera.core import *
from gamera.plugins.listutilities import median
def my_filter(imageIn):
	count = 0
	image = imageIn
	ccs = image.cc_analysis()
	print "filter started on",len(ccs) ,"elements..."
	median_black_area = median([cc.black_area()[0] for cc in ccs])
	#also check for height?
	for cc in ccs:
		if(cc.black_area()[0] > (median_black_area * 5)):
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

def filter_and_bbox(imageIn):
   from gamera.toolkits.ocr.classes import Page
   my_filter(imageIn)
   p = Page(imageIn)
   p.segment()
   return show_lines(p)

def my_application():
   from gamera.toolkits.ocr.classes import Page
   # Make the image variable a global variable
   # IF YOU DON'T DO THIS, THE WINDOW WILL DISAPPEAR!
   global image, ots, ots_up, ots_mid, box_image
   picture = mh.imread(sys.argv[-1], as_grey=True)
   picture = picture.astype(np.uint8)
   # Load the image
   image = numpy_io.from_numpy(picture)#load_image(sys.argv[-1])
	
   # Display the image in a window
   #image.simple_sharpen()
   ots = image.otsu_threshold()
   thresh = image.otsu_find_threshold()
   thresh_mid = int(thresh * 1.05)
   thresh_plus = int(thresh * 1.15)
   ots_up = image.threshold(thresh_plus)
   ots_mid = image.threshold(thresh_mid)
   
   print "OTSU: " + str(thresh)
   print "OTSU Mid: " + str(thresh_mid)
   print "OTSU * 1.15: " + str(thresh_plus)
   
   ots = filter_and_bbox(ots)
   ots_up = filter_and_bbox(ots_up)
   ots_up.display("OTSU+")
   #ots_mid = show_lines(p)
   #box_image.display()
   #my_filter(ots_mid)
   #ots_up.display("OTSU+FIL")
   ots_mid = filter_and_bbox(ots_mid)
   ots_mid.display("MID")
   ots.display("OTSU")
   image.display()
# Import the Gamera core and initialize it
from gamera.core import *
init_gamera()

# Import the Gamera GUI and start it
from gamera.gui import gui
gui.run(my_application)

# The GUI thread will automatically stop when all windows have
# been closed.
print "Goodbye!"

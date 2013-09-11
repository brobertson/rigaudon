#!/usr/local/python/bin/python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 3 -*-
# vim: set tabstop=3 shiftwidth=3 expandtab:

# Copyright (C) 2010-2011 Christian Brandt
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


# This just simply runs the greekocr toolkits main function
import string, re, sys, os
from gamera.core import *
from gamera.plugins.listutilities import median
from gamera.toolkits.greekocr import GreekOCR
from gamera.plugins import pagesegmentation
from gamera.toolkits.ocr.classes import Page
from gamera.toolkits.greekocr.singlediacritics import *

class MyPage(Page):
   def page_to_lines(self):
      #offset_x = 566, offset_y = 105, ncols = 622, nrows = 28
      self.ccs_lines = []
      label  = 1
      seg_rect = Rect(Point(556, 105), Dim(622, 28))
      new_seg = Cc(self, label, seg_rect.ul, seg_rect.lr)
      self.ccs_lines.append(new_seg)



def usage():
   usage = "Usage:\n"
   usage += "  greekocr4gamera.py -x <traindata> [options] <imagefile>\n"
   usage += "\n"
   usage += "  Options:\n"
   usage += "   --wholistic          wholistic segmentation mode (default)\n"
   usage += "   -w                   short for --wholistic\n"
   usage += "   --separatistic       separatistic segmentation mode\n"
   usage += "   -s                   short for --separatistic\n"
   usage += "\n"
   usage += "   --unicode <file>     specify filename for unicode output\n"
   usage += "   -u <file>            short for --unicode\n"
   usage += "   --teubner <file.tex> specify filename for teubner TeX output\n"
   usage += "   -t <file>            short for --teubner\n"
   usage += "\n"
   usage += "   --deskew             do a skew correction (recommended)\n"
   usage += "   --filter             filter out very large (images) and very\n" 
   usage += "                        small components (noise)\n"
   usage += "\n"
   usage += "   --debug              save debug-images\n"
   usage += "                        debug_lines.png debug_words.png debug_chars.png\n"
   usage += "   -d                   short for --debug\n"
   usage += "\n"
   usage += "  --split               perform splitting on elements so designated\n"
   usage += "                        by the classifier. (Added by BGR)"
   usage += "  --autogroup           perform 'autogrouping', wherein the ocr engine\n"
   usage += "                        attempts to join discrete elements into known\n"
   usage += "                        glyphs. This is very costly, but necessary when\n"
   usage += "                        when the scan is light. (Added by BGR)"
   
   usage += "\n"
   usage += "  --hocr               specify a filename or filenames for hocr input\n"

   usage += "                       this xhtml file's line-splitting data will be\n"
   usage += "                       then used rather than Gamera's own. If using\n"
   usage += "                       the --dir option, a %s in this paramter will\n"
   usage += "                       be substituted with the basename of the current\n"
   usage += "                       input file.\n" 
   usage += "\n"
   usage += "  --otsu               specify a comma-separated list of factors by\n"
   usage += "                       which the Otsu threshold will be multiplied \n"
   usage += "                       to make a new binary image.\n"
   
   sys.stderr.write(usage)

def performGreekOCR(options):
   import mahotas as mh
   import numpy as np
   from pylab import imshow, gray, show
   #from os import path
   from gamera.plugins import numpy_io
#   features = ["aspect_ratio", "volume64regions", "moments", "nholes_extended"]   
#I think these are size-invariant
#   features = ["aspect_ratio","moments","nholes","nholes_extended","skeleton_features","top_bottom","volume","volume16regions","volume64regions","zernike_moments"]
   MAX_CCS = 6500
   features = ["aspect_ratio","moments","ncols_feature","nholes","nholes_extended","nrows_feature","skeleton_features","top_bottom","volume","volume16regions","volume64regions","zernike_moments"]
   image_files = []
   g = GreekOCR(splits=options["split"],feats=features)
   g.mode = options["mode"] + "body"
   g.autogroup = options["autogroup"]
   g.debug = options["debug"] 
   g.load_trainingdata(options['trainingdata'])
   g_appcrit = GreekOCR(splits=options["split"], feats=features)
   g_appcrit.mode = options["mode"] + "appcrit"
   g_appcrit.autogroup = options["autogroup"]
   g_appcrit.debug = options["debug"]
   g_appcrit.load_trainingdata(options['trainingdata'])
   
   if options["hocrfile"]:
      g.hocr = (options["hocrfile"])
   if options["settingsfile"]:
      g.load_settings(options["settingsfile"])
      g_appcrit.load_settings(options["settingsfile"])
   if options["otsu"]:
      otsu_factors_string = options["otsu"].split(',')
      otsu_factors = [float(x) for x in otsu_factors_string]
   else:
      otsu_factors = [0]
   if options["directory"]:
      image_files = os.listdir(options["directory"])
      image_files = [os.path.join(options["directory"],x) for x in image_files]
      test = re.compile(".png$",re.IGNORECASE)
      image_files = filter(test.search, image_files)
      image_files.sort()
   elif options["imagefile"]:
      image_files = options["imagefile"]
   image_file_count = 1;
   image_path = os.path.abspath(image_files[0])
   image_split_path = os.path.split(image_path)
   book_code = os.path.split(image_split_path[0])[1]
   book_id = 0
   if options.has_key("sql") and options["sql"]:
      book_id = sql_make_book_and_return_id(book_code)
  # if options.has_key("hocrout") and options["hocrout"]:
  #     hocr_tree = hocr_make_tree_and_return(book_code)
   for image_file in image_files:

      image_path = os.path.abspath(image_file)
      image_split_path = os.path.split(image_path)
      book_code = os.path.split(image_split_path[0])[1]#directory name
      image_file_name = image_split_path[1]
      imageBase, imageEx = os.path.splitext(image_file_name)
      threshold_info = ""
      print "Now working with image: " + image_file_name
      internal_image_file_path = os.path.join(book_code, image_file_name) 
      if imageEx == ".jp2":
         try:
            jp2Image = mh.imread(image_file, as_grey=True)
            jp2Image = jp2Image.astype(np.uint8)
            imageIn = numpy_io.from_numpy(jp2Image)
         except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
      else:
         try:
            imageIn = load_image(image_file)
         except:
            continue
      imageType = imageIn.data.pixel_type
      if imageType != ONEBIT:
         if imageType != GREYSCALE:
            imageIn = imageIn.to_greyscale()
         otsu_thresh = imageIn.otsu_find_threshold()
      for otsu_factor in otsu_factors:
         if options.has_key("hocrout") and options["hocrout"]:
            hocr_tree = hocr_make_tree_and_return(book_code)
         if imageIn.data.pixel_type == ONEBIT:
            threshold_info = "thresh_128"
            otsu_thresh = 1.0
            image = imageIn
            if options["debug"]:
               print "image is ONEBIT; doing no threshold optimization."
         else:
            current_thresh = otsu_thresh * otsu_factor
            if current_thresh > 253.0:
               current_thresh = 253.0
            current_thresh = int(current_thresh)
            threshold_info = "thresh_" + str(int(current_thresh))# + "=" + str(otsu_factor)
            image = imageIn.threshold(current_thresh)
            print "Otsu factor: ", otsu_factor, " threshold: ", current_thresh
         if options["hocrfile"]:
            hocr_to_use = string.replace(options["hocrfile"],"%s",imageBase)
            g.hocr = hocr_to_use
            if options["debug"]:
               print "using '" + hocr_to_use + "' as hocr file"
         if options.has_key("filter") and options["filter"] == True:
             count = 0
             ccs = image.cc_analysis()
             if options.has_key("debug"):
                if options["debug"] == True:
                   print "filter started on",len(ccs) ,"elements..."
             #filter long vertical runs left over from margins
	     
	          
##               #Agressive run filtering
##               median_height = median([cc.nrows for cc in ccs])
##               for cc in ccs:
##               #TODO: add another condition that keeps these at edges of page
##                       if((cc.nrows / cc.ncols > 6) and (cc.nrows > 1.5 * median_height) ):
##                               cc.fill_white()
##                               del cc
##                               count = count + 1
             median_black_area = median([cc.black_area()[0] for cc in ccs])
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
             if options.has_key("debug") and options["debug"] == True:
                print "filter done.",len(ccs)-count,"elements left."
         if (len(ccs) < 5) or (len(ccs) > MAX_CCS):
                 print "Error: there are " + str(len(ccs)) +  " ccs. Max is " + str( MAX_CCS) +  " Omitting this image."
		 #raise ImageSegmentationError("Error: there are " + str(len(ccs)) +  " ccs. Max is " + str( MAX_CCS) +  " Omitting this image.")
         else:
            if options.has_key("deskew") and options["deskew"] == True:
              #from gamera.toolkits.otr.otr_staff import *
              if options.has_key("debug") and options["debug"] == True:
                print "\ntry to skew correct..."
              rotation = image.rotation_angle_projections(-10,10)[0]
              img = image.rotate(rotation,0)
              if options.has_key("debug") and options["debug"] == True:
                print "rotated with",rotation,"angle"
            if options.has_key("mode") and options["mode"] == "teubner":
               (body_image, app_crit_image) = splitAppCritTeubner(image)
               output = g.process_image(body_image)
               if app_crit_image:
                  print "there is an app. crit image"
                  appcrit_output = g_appcrit.process_image(app_crit_image)
               else:
                  print "there is no app. crit image"
                  appcrit_output = ""
               output = output + appcrit_output
            else:
               output = g.process_image(image) 
            output_file_name_base = options["unicodeoutfile"] + imageBase + "_" +imageEx[1:] + "_" + threshold_info
            if options.has_key("debug") and options["debug"] == True:
               g.save_debug_images(output_file_name_base)
               if options.has_key("mode") and options["mode"] == "teubner" and app_crit_image:
                  #TODO: make more general
                  g_appcrit.save_debug_images(output_file_name_base + "_appcrit")
            if options.has_key("hocrout") and options["hocrout"]:
               #if we turned this on, we would make a separate div for each page of input
               #hocr_tree = hocr_make_page_and_return_div(internal_image_file_path,image_file_count,book_id,hocr_tree)
               g.store_hocr(internal_image_file_path,hocr_tree)
               if options.has_key("mode") and options["mode"] == "teubner" and app_crit_image:
                  g_appcrit.store_hocr(internal_image_file_path,hocr_tree)
            if options.has_key("sql") and options["sql"]:
               page_id = sql_make_page_and_return_id(internal_image_file_path,image_file_count,book_id)
               g.store_sql(image_path,page_id) 
            if options.has_key("unicodeoutfile"):
                
               if options.has_key("hocrout") and options["hocrout"]:
                  g.save_text_hocr(hocr_tree, output_file_name_base + ".html")
               else:
                  g.save_text_unicode( output_file_name_base + ".txt")
                  if options.has_key("mode") and options["mode"] == "teubner":
                     #TODO: make the above more general
                     g_appcrit.save_text_unicode( output_file_name_base + "_appcrit.txt")
            elif options.has_key("teubneroutfile"):
               g.save_text_teubner(options["teubneroutfile"])
            else:
               print output
      image_file_count += 1

def splitAppCritTeubner(imageIn):
   from gamera.toolkits.ocr.classes import Page
   image2 = imageIn.image_copy()
   p = FindAppCritTeubner(imageIn)
   p.segment()
   #print "image width: " + str(imageIn.ncols)
   s = sorted(p.ccs_lines, key=lambda cc: cc.offset_y)
   s.reverse()
   x = 0 
   for cc in s:
   	#has to be reasonably wide, and not higher than 2/3 down the page
   	x = x + 1
   	if cc.ncols > 0.6 * imageIn.ncols and cc.offset_y > 0.6 * imageIn.nrows:
   		#print "Image rows: " + str(imageIn.nrows)
   		#print str(cc.ncols) + "x" + str(cc.offset_y)
   		cc.fill_white()
   		break
   
   im = imageIn.image_copy()
   im.reset_onebit_image()
   #print "x = " + str(x)
   #print len(s)
   if x == len(s):
   	#then there wasn't an app. crit found
   	#print "no app crit found"
   	q = None
   else:
      q = only_app_crit(image2, x)
   return (im,q)
   
def only_app_crit(imageIn, xIn):
   from gamera.toolkits.ocr.classes import Page
   p = FindAppCritTeubner(imageIn)
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
   return im

def hocr_make_tree_and_return(book_code):
   import lxml
   from lxml import etree
   import StringIO
   tree = etree.parse(StringIO.StringIO('''<?xml version="1.0"?>
   <!DOCTYPE html
   PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <meta content="riguadon 0.3" name="ocr-system"/>
   <meta name="ocr-number-of-pages" content="1"/>
   <meta name="ocr-langs" content="grc lat"/>
     <meta content="ocr_line ocr_page" name="ocr-capabilities"/>
    <title>OCR Output</title>
    </head>
   <body/>
    </html>
    '''))
   
#   para = etree.SubElement(body, "{http://www.w3.org/1999/xhtml}p")
#   para2 = etree.SubElement(body, "{http://www.w3.org/1999/xhtml}p")
#   para2.text="two"
#   para2.set("class","foo")
#   para2.set("title","a b c d e")
   return tree
 

def sql_make_book_and_return_id(book_code):
   import mySQLdb
   db = MySQLdb.connect(host="localhost", user="root", passwd="Password", db="squeegee_development",use_unicode=True)
   cursor = db.cursor()
   db.set_character_set('utf8')
   cursor.execute('SET NAMES utf8;')
   cursor.execute('SET CHARACTER SET utf8;')
   cursor.execute('SET character_set_connection=utf8;')
   db.commit()
   try:
      cursor.execute("select id from books where googleId = %s",book_code)
      r = cursor.fetchone()
      id_out = r[0]
      return id_out
   except TypeError: #ok, there is no record of that name, so let's make one.
      cursor.execute("""insert into books (googleId) VALUES (%s)""",(book_code))
      db.commit()
      cursor.execute("select id from books where googleId = %s",book_code)
      r = cursor.fetchone()
      id_out = r[0]
      return id_out


def sql_make_page_and_return_id(page_path,number,book_id):
   import mySQLdb
   db = MySQLdb.connect(host="localhost", user="root", passwd="Password", db="squeegee_development",use_unicode=True)
   cursor = db.cursor()
   db.set_character_set('utf8')
   cursor.execute('SET NAMES utf8;')
   cursor.execute('SET CHARACTER SET utf8;')
   cursor.execute('SET character_set_connection=utf8;')
   db.commit()
   cursor.execute("""insert into pages (url,number,book_id) VALUES (%s,%s,%s)""",(page_path,number,book_id))
   db.commit()
   cursor.execute("select id from pages where url = %s",page_path)
   r = cursor.fetchone()
   id_out = r[0]
   return id_out
   
   def store_sql(self):
      import mySQLdb
      myDb,myCursor = self.getCursor()
      x = 0 
      print "processing tuples..."
      for t in self.word_tuples:
         if not (t[0] == u'\n'):
            foo = self.lowerStripAccents(t[0]).encode('utf-8')
            bar = t[0].encode('utf-8')
            myCursor.execute("INSERT INTO scanned_words (polyForm,form,page_id,number,meanConfidence,tlX,tlY,brX,brY) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(bar,foo,3,x,0.55,t[1][0].ul_x,t[1][0].ul_y,t[1][len(t[1])-1].lr_x,t[1][len(t[1])-1].lr_y))
            print t[0].encode('utf-8')
            x = x + 1
      myDb.commit()
      myCursor.close()

   def getCursor():
      import MySQLdb
      db = MySQLdb.connect(host="localhost", user="root", passwd="Password", db="squeegee_development",use_unicode=True)
      cursor = db.cursor()
      db.set_character_set('utf8')
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')
      db.commit()
      return db, cursor
  
#begin main program
options = {}
args = sys.argv[1:]

i = 0
options["imagefile"] = []
while i < len(args):
   if args[i] in ("-x", "--trainingdata"):
      i += 1
      options["trainingdata"] = args[i]
   elif args[i] in ("--help", "-h"):
      usage()
   elif args[i] in ("--wholistic", "-w"):
      options["mode"] = "wholistic"
   elif args[i] in ("--separatistic", "-s"):
      options["mode"] = "separatistic"
   elif args[i] in ("-u","--unicode"):
      i += 1
      options["unicodeoutfile"] = args[i]
   elif args[i] in ("-t", "--teubner"):
      i += 1
      options["teubneroutfile"] = args[i]
   elif args[i] in ("-d", "--debug"):
      options["debug"] = True
   elif args[i] in ("--deskew"):
      options["deskew"] = True
   elif args[i] in ("--filter"):
      options["filter"] = True
   elif args[i] in ("--split"):
      options["split"] = 1 
   elif args[i] in ("--autogroup", "-g"):
      options["autogroup"] = True
   elif args[i] in ("--profile"):
      options["profile"] = True
   elif args[i] in ("--sql"):
      options["sql"] = True      
   elif args[i] in ("--hocr"):
      i += 1
      options["hocrfile"] = args[i]
   elif args[i] in ("--settings"):
      i += 1
      options["settingsfile"] = args[i]
   elif args[i] in ("--dir"):
      i += 1
      options["directory"] = args[i]
   elif args[i] in ("--otsu"):
      i+= 1
      options["otsu"] = args[i]
   elif args[i] in ("--mode"):
      i+=1
      options["mode"] = args[i]
   elif args[i] in ("--hocrout"):
      options["hocrout"] = True
   else:
      options["imagefile"].append(args[i])
   i += 1

if options.has_key("directory"):
   if (not os.path.isdir(options["directory"])):
      print 'Directory "{0}" not accesible.'.format(options["directory"])
      usage()
      exit(1)
else:
   options["directory"] = None

if not (options.has_key("imagefile") or options.has_key("directory")):
   print 'Input image file or directory not provided.'
   usage()
   exit(1)

if not options.has_key("otsu"):
   options["otsu"] = "1" 
if options.has_key("settingsfile"):
   try:
      with open(options["settingsfile"]) as f: pass
   except IOError as e:
      print 'Settings file "{0}" not accesible.'.format(options["settingsfile"])
      usage()
      exit(1)
else:
   options["settingsfile"] = None

if options.has_key("hocrfile"):
   #Don't test for a real file if the input contains a substitution
   #variable. 
   if (not "%s" in options["hocrfile"]):
      try:
         with open(options["hocrfile"]) as f: pass
      except IOError as e:
         print 'Hocr file "{0}" not accesible.'.format(options["hocrfile"])
         usage()
         exit(1)
else:
   options["hocrfile"] = None

if not options.has_key("debug"):
   options["debug"] = False 
if not options.has_key("split"):
   options["split"] = 0
if not options.has_key("trainingdata"):
   print "No Trainingdata given"
   usage()
   exit(1)

if not options.has_key("mode"):
   options["mode"] = "separatistic"
if not options.has_key("autogroup"):
   options["autogroup"] = False
if not options.has_key("profile"):
   options["profile"] = False

#an option to profile the process
if options["profile"]:
   import cProfile
   import pstats
   cProfile.run("performGreekOCR(options)",'profile')
   p = pstats.Stats('profile')
   p.sort_stats('cumulative').print_stats(20)
else:
   performGreekOCR(options)

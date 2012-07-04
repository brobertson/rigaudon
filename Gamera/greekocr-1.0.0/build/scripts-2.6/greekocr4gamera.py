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
import re, sys, os
from gamera.core import *
from gamera.plugins.listutilities import median
from gamera.toolkits.greekocr import GreekOCR
from gamera.plugins import pagesegmentation
from gamera.toolkits.ocr.classes import Page

class MyPage(Page):
   def page_to_lines(self):
       self.ccs_lines = self.img.bbox_merging(1,10)



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
   sys.stderr.write(usage)

def performGreekOCR(options):
#   features = ["aspect_ratio", "volume64regions", "moments", "nholes_extended"]   
   features = ["aspect_ratio","moments","nholes","nholes_extended","skeleton_features","top_bottom","volume","volume16regions","volume64regions","zernike_moments"]
 #  features = ["aspect_ratio","moments","ncols_feature","nholes","nholes_extended","nrows_feature","skeleton_features","top_bottom","volume","volume16regions","volume64regions","zernike_moments"]
   image_files = []
   g = GreekOCR(splits=options["split"],feats=features)
   g.mode = options["mode"]
   g.autogroup = options["autogroup"]
   g.debug = True
   g.load_trainingdata(options['trainingdata'])
   if options.has_key("settingsfile"):
      g.load_settings(options["settingsfile"])
   if options.has_key("directory"):
      image_files = os.listdir(options["directory"])
      image_files = [os.path.join(options["directory"],x) for x in image_files]
      test = re.compile(".png$",re.IGNORECASE)
      image_files = filter(test.search, image_files)
      image_files.sort()
   elif options.has_key("imagefile"):
      image_files = [options["imagefile"]]
   image_file_count = 1;
   image_path = os.path.abspath(image_files[0])
   image_split_path = os.path.split(image_path)
   book_code = os.path.split(image_split_path[0])[1]
   book_id = 0
   if options.has_key("sql") and options["sql"]:
      book_id = sql_make_book_and_return_id(book_code)
   for image_file in image_files:
      image_path = os.path.abspath(image_file)
      image_split_path = os.path.split(image_path)
      book_code = os.path.split(image_split_path[0])[1]#directory name
      image_file_name = image_split_path[1]
      internal_image_file_path = os.path.join(book_code, image_file_name) 
      image = load_image(image_file)
      if image.data.pixel_type != ONEBIT:
         image = image.to_onebit()
      if options.has_key("filter") and options["filter"] == True:
          count = 0
          ccs = image.cc_analysis()
          if options.has_key("debug") and options["debug"] == True:
             print "filter started on",len(ccs) ,"elements..."
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
      
      
      if options.has_key("deskew") and options["deskew"] == True:
        #from gamera.toolkits.otr.otr_staff import *
        if options.has_key("debug") and options["debug"] == True:
          print "\ntry to skew correct..."
        rotation = image.rotation_angle_projections(-10,10)[0]
        img = image.rotate(rotation,0)
        if options.has_key("debug") and options["debug"] == True:
          print "rotated with",rotation,"angle"
      
      
      if options.has_key("columns") and options["columns"] == True:
         blocks = image.bbox_merging(1,10) 
         output = ""
         # these aren't actually 'lines', they are probably parts of 
         # the page
         print "doing blocks. Count " + str(len(blocks))
         #partial_images = [block.image_copy() for block in blocks]
         partial_images = []
         for block in blocks:
            im = block.image_copy()
            im.reset_onebit_image()
            partial_images.append(im)
         print("Hello everyone")
         for partial_image in partial_images:
            output = g.process_image(partial_image)
      else:      
         output = g.process_image(image)
      if options.has_key("debug") and options["debug"] == True:
         g.save_debug_images()
         
      if options.has_key("sql") and options["sql"]:
         page_id = sql_make_page_and_return_id(internal_image_file_path,image_file_count,book_id)
         g.store_sql(image_path,page_id) 
      if options.has_key("unicodeoutfile"):
         g.save_text_unicode(options["unicodeoutfile"] )#+ str(image_file_count) + ".txt")
      elif options.has_key("teubneroutfile"):
         g.save_text_teubner(options["teubneroutfile"])
      else:
         print output
      image_file_count += 1

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
      print("filtering!")
      options["filter"] = True
   elif args[i] in ("--split"):
      options["split"] = 1 
   elif args[i] in ("--autogroup", "-g"):
      options["autogroup"] = True
   elif args[i] in ("--profile"):
      options["profile"] = True
   elif args[i] in ("--sql"):
      options["sql"] = True      
   elif args[i] in ("--columns"):
      options["columns"] = True
      print("doing columns, apparently")
   elif args[i] in ("--settings"):
      i += 1
      options["settingsfile"] = args[i]
   elif args[i] in ("--dir"):
      i += 1
      options["directory"] = args[i]
   else:
      options["imagefile"] = args[i]
   i += 1

if not options.has_key("split"):
   options["split"] = 0
if not options.has_key("trainingdata"):
   print "No Trainingdata given"
   usage()
   exit(1)
if not options.has_key("mode"):
   options["mode"] = "wholistic"
if not options.has_key("autogroup"):
   options["autogroup"] = False
if not options.has_key("profile"):
   options["profile"] = False
if not options.has_key("imagefile"):
   print "No filename given"
   usage()
   exit(2)
if options["profile"]:
   import cProfile
   import pstats
   cProfile.run("performGreekOCR(options)",'profile')
   p = pstats.Stats('profile')
   p.sort_stats('cumulative').print_stats(20)
else:
   performGreekOCR(options)

class MyPage(Page):
   def page_to_lines(self):
       self.ccs_lines = self.img.bbox_merging(1,10)




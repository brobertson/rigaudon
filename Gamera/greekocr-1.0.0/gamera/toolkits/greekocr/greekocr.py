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

import pprint
from gamera.core import * 
init_gamera()    
from gamera import knn   
from gamera.plugins import pagesegmentation
from gamera.plugins.pagesegmentation import textline_reading_order
from gamera.classify import ShapedGroupingFunction
from gamera.plugins.image_utilities import union_images
from gamera.toolkits.ocr.ocr_toolkit import *
from gamera.toolkits.ocr.classes import Textline,Page,ClassifyCCs
from gamera.gamera_xml import glyphs_to_xml
from gamera.knn_editing import edit_cnn

from gamera.toolkits.greekocr.singlediacritics import *
from gamera.toolkits.greekocr.wholisticdiacritics import *
import unicodedata
import codecs



def clean_classifier(cknn):
   glyphs = cknn.get_glyphs()
   print "old %d" % len(glyphs)
   sorted_glyphs = sorted(glyphs, key=lambda g: g.to_rle())
   new_glyphs = []
   
   last_rle = sorted_glyphs[0].to_rle()
   new_glyphs.append(sorted_glyphs[0])
   for i in range(1, len(sorted_glyphs) -1):
         if last_rle != sorted_glyphs[i].to_rle():
            new_glyphs.append(sorted_glyphs[i])
         else:
            print sorted_glyphs[i].get_main_id()
   
   print "new after removing duplicates: %d" % len(new_glyphs)
   cknn.set_glyphs(new_glyphs)
   cknn = edit_cnn(cknn)
   
   print "new after cnn: %d" % len(cknn.get_glyphs())
   return cknn

class AgressivePager(SinglePage):
   def page_to_lines(self):
      self.ccs_lines = self.img.bbox_mcmillan(section_search_size=6)


class GreekOCR(object):
   """Provides the functionality for GreekOCR. The following parameters
control the recognition process:

  **cknn**
    The kNNInteractive classifier.

  **mode**
    The mode for dealing with accents.
    Can be ``wholistic`` or ``separatistic``.
"""
   def __init__(self, mode="wholistic", splits=0, feats=["aspect_ratio", "volume64regions", "moments", "nholes_extended"]):
      """Signature:

   ``init (mode="wholistic")``

where *mode* can be "wholistic" or "separatistic".
"""
      self.optimizeknn = False
      self.debug = False
      self.cknn = knn.kNNInteractive([], feats, splits)
      self.autogroup = False
      self.output = ""
      self.mode = mode
      


   def load_trainingdata(self, trainfile):
      """Loads the training data. Signature:

   ``load_trainingdata (trainfile)``

where *trainfile* is an Gamera XML file containing training data.
Make sure that the training file matches the *mode* (wholistic
or separatistic).
"""
      self.cknn.from_xml_filename(trainfile)
      if self.optimizeknn:
         self.cknn = clean_classifier(self.cknn)
     


   def segment_page(self):
      if (self.mode != "separatistic"):
         self.page = WholisticPage(self.img)

      if self.debug:
         print "start page segmentation..."
         t = time.time()

      #cknn = knn.kNNInteractive([], ["aspect_ratio", "volume64regions", "moments", "nholes_extended"], 0)
      #cknn.from_xml_filename(trainfile)
      the_ccs = self.img.cc_analysis()
      median_cc = int(median([cc.nrows for cc in the_ccs]))
      if (self.autogroup):
        autogroup = ClassifyCCs(self.cknn)
        autogroup.parts_to_group = 4 
        autogroup.grouping_distance = max([2,median_cc / 2])
        if self.debug:
          print "autogroup distance: ", autogroup.grouping_distance
       # self.page = AgressivePager(self.img, classify_ccs=autogroup)
        self.page = SinglePage(self.img, classify_ccs=autogroup)
      else:
        self.page = SinglePage(self.img, classify_ccs=autogroup)
       # self.page = AgressivePager(self.img)
      self.page.segment()
      pp = pprint.PrettyPrinter(indent=4,depth=10)
      if self.debug:
         print "Page representation: "
         print self.page.__dict__
         print self.page.textlines[0].__dict__
      if self.debug:
         t = time.time() - t
         print "\t segmentation done [",t,"sec]"



   def get_page_glyphs(self, image):
      """Returns a list of segmented CCs using the selected segmentation 
approach on the given image. This list can be used for creating training data.
Signature:

   ``get_page_glyphs (image)``

where *image* is a Gamera image. 
"""
      if image.data.pixel_type != ONEBIT:
         image = image.to_onebit()
      self.img = image

      self.segment_page()
      glyphs = [] 
      for line in self.page.textlines:
         for g in line.glyphs:
            glyphs.append(g)

      return glyphs

      
   def save_debug_images(self):
      """Saves the following images to the current working directory:

  **debug_lines.png**
    Has a frame drawn around each detected line.

  **debug_chars.png**
    Has a frame drawn around each detected character.

  **debug_words.png**
    Has a frame drawn around each detected word.
"""
      rgbfilename = "debug_lines.png"
      rgb = self.page.show_lines()
      rgb.save_PNG(rgbfilename)
      print "file '%s' written" % rgbfilename
      rgbfilename = "debug_chars.png"
      rgb = self.page.show_glyphs()
      rgb.save_PNG(rgbfilename)
      print "file '%s' written" % rgbfilename
      rgbfilename = "debug_words.png"
      rgb = self.page.show_words()
      rgb.save_PNG(rgbfilename)
      print "file '%s' written" % rgbfilename



   def classify_text(self):
      self.word_tuples = []
      self.output = ""
      for line in self.page.textlines:
         line.glyphs = \
            self.cknn.classify_and_update_list_automatic(line.glyphs)
         line.sort_glyphs()
         self.word_tuples = self.word_tuples + line.to_word_tuples() + [(u'\n',None)]
      for t in self.word_tuples:
         self.output = self.output + t[0]
         if not (t[0] == u'\n'):
            self.output = self.output + " "
      self.output = self._normalize(self.output) 

   def lowerStripAccents(self,word):
      import unicodedata
	   wordOut = []
	   sigma = unichr(963)
	   word = word.lower()
	   for char in word:
	   	cat = unicodedata.category(char)
	   	if (cat[0] == 'L'):
	   		charNum = ord(char)
	   		if (charNum == 962):
		   		wordOut.append(sigma)
		   	else:
		   		wordOut.append(char)
	   return u''.join(wordOut) 

   def get_text(self):
      return self.output

   def store_sql(self,image_path,page_id):
      myDb,myCursor = self.getCursor()
      x = 0 
      print "processing tuples..."
      for t in self.word_tuples:
         if not (t[0] == u'\n'):
            form = self.lowerStripAccents(t[0]).encode('utf-8')
            polyForm = t[0].encode('utf-8')
            smallest_x, smallest_y, biggest_x, biggest_y = self.getBounds(t[1])
            myCursor.execute("INSERT INTO scanned_words (polyForm,form,page_id,number,meanConfidence,tlX,tlY,brX,brY) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(polyForm,form,page_id,x,0.55,smallest_x,smallest_y,biggest_x,biggest_y))
            myCursor.execute("SELECT LAST_INSERT_ID()")
            r = myCursor.fetchone()
            sw_id = r[0]
            print "list_insert_id(): ", sw_id
            myCursor.execute("""SELECT form from scanned_words where id = %s """, sw_id)
            r = myCursor.fetchone()
            form_from_sql = r[0]# for some reason, this needs to be done indirectly, not using the 'form' variable above
            #print t[0].encode('utf-8')
            #print "form from sql: ", form_from_sql
            myCursor.execute("""SELECT id from entries where form = %s """,form_from_sql)
            rows = myCursor.fetchall()
            for row in rows:
               print "found row: ", row[0]
               myCursor.execute("INSERT INTO entries_scanned_words (entry_id, scanned_word_id) VALUES (%s,%s)",(row[0],sw_id))
             #  myDb.commit()
            x = x + 1
      myDb.commit()
      myCursor.close()

   def getBounds(self,glyph_list):
      smallest_x = smallest_y = sys.maxint
      biggest_x = biggest_y = 0
      for glyph in glyph_list:
         if glyph.ul_x < smallest_x:
            smallest_x = glyph.ul_x
         if glyph.lr_x > biggest_x:
            biggest_x = glyph.lr_x
         if glyph.ul_y < smallest_y:
            smallest_y = glyph.ul_y
         if glyph.lr_y > biggest_y:
            biggest_y = glyph.lr_y
      return smallest_x, smallest_y, biggest_x, biggest_y
   
   def getCursor(self):
      import MySQLdb
      self.db = MySQLdb.connect(host="localhost", user="root", passwd="Password", db="squeegee_development",use_unicode=True)
      self.cursor = self.db.cursor()
      self.db.set_character_set('utf8')
      self.cursor.execute('SET NAMES utf8;')
      self.cursor.execute('SET CHARACTER SET utf8;')
      self.cursor.execute('SET character_set_connection=utf8;')
      self.db.commit()
      return self.db, self.cursor


   def process_image(self, image):
      """Recognizes the given image and returns the recognized text
as Unicode string. Signature:

   ``process_image (image)``

where *image* is a Gamera image. The recognized text is additionally stored
in the ``GreekOCR`` property *output*, which can subsequently be written to
a file with save_text_unicode_ or save_text_teubner_.

Make sure that you have called load_trainingdata_ before!
"""
      if image.data.pixel_type != ONEBIT:
         image = image.to_onebit()
      self.img = image
      if self.debug:
         print "Doing page Segmentation"
      self.segment_page()
      if self.debug:
         print "Classifying Text"
      self.classify_text()
      #if self.debug:
      #   print "storing to database"
     # self.store_sql()
      #if self.debug:
      #   print "Returning Output"
      return self.get_text()
      


   def save_text_xetex(self, filename):
      data = \
'''\documentclass[11pt]{article}
\usepackage{xltxtra}
\setmainfont[Mapping=tex-text]{GFS Porson}
\\begin{document}
%s
\end{document}''' % self.output.replace("\n", "\n\n")

      f = codecs.open(filename, "w", encoding='utf-8')
      f.write(data)
      f.close()
      


   def save_text_unicode(self, filename):
      """Stores the recognized text to the given *filename* as Unicode string.
Signature

   ``save_text_unicode(filename)``

Make sure that you have called process_image_ before!
"""
      f = codecs.open(filename, "w", encoding='utf-8')
      f.write(self.output)
      f.close()



   def save_text_teubner(self, filename):
      """Stores the recognized text to the given *filename* as a LaTeX
document utilizing the Teubner style for representing Greek characters and
accents.
Signature

   ``save_text_teubner(filename)``

Make sure that you have called process_image_ before!
"""
      from unicode_teubner import unicode_to_teubner

      data = '''
\documentclass[10pt]{article}
\usepackage[polutonikogreek]{babel}
\usepackage[or]{teubner}
\\begin{document}
\selectlanguage{greek}
%s
\end{document}
''' % unicode_to_teubner(self.output).replace("\n", "\n\n")

      f = codecs.open(filename, "w", encoding='utf-8')
      f.write(data)
      f.close()



   
   def _normalize(self,str):
      str = unicodedata.normalize("NFD", str)
      output = u""
      combined = []
      for i in str:
         is_combining = True
         try:
            is_combining = unicodedata.combining(i) > 0 or unicodedata.name(i).find("ACCENT") >= 0
         except:
            is_combining = False
         if not is_combining:
            for j in sorted(combined):
               output += j
            combined = []
            output += i
         else:
            combined.append(i)
   
      if len(combined) > 0:
         for j in sorted(combined):
            output += j
      return unicodedata.normalize("NFD", output)


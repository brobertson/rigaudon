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

from gamera.toolkits.greekocr.hocr_segmentation import *
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

class HocrPager(SinglePage):
   hocr = None
   def __init__(self, image, glyphs=None, classify_ccs=None, hocr="hi there"):
      self.hocr = hocr
      SinglePage.__init__(self,image,glyphs,classify_ccs)
   def page_to_lines(self):
      lineParser = SpanLister('ocr_line')
      try:
         lineParser.feed(open(self.hocr).read())
      except IOError as e:
         print "Error: could not open hocr file '" + self.hocr + "'"
         print "Exiting."
         exit(1) 
      self.ccs_lines =  generateCCsFromHocr(lineParser,self.img)

class GreekOCR(object):
   """Provides the functionality for GreekOCR. The following parameters
control the recognition process:

  **cknn**
    The kNNInteractive classifier.

  **mode**
    The mode for dealing with accents.
    Can be ``wholistic`` or ``separatistic``.
"""
   def __init__(self, mode="wholistic", splits=0, feats=["aspect_ratio", "volume64regions", "moments", "nholes_extended"], hocr=None):
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
      self.hocr = hocr
      


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
     
   def load_settings(self, settingsfile):
      self.cknn.load_settings(settingsfile)

   def segment_page(self):
      if (self.mode != "separatistic"):
         self.page = WholisticPage(self.img)
      if self.debug:
         #time start of page segmentation
         t = time.time()
      the_ccs = self.img.cc_analysis()
      median_cc = int(median([cc.nrows for cc in the_ccs]))
      if self.debug:
         print self.mode
      if (self.autogroup):
        autogroup = ClassifyCCs(self.cknn)
        autogroup.parts_to_group = 4 
        autogroup.grouping_distance = max([2,median_cc / 2])
        if self.debug:
          print "autogroup distance: ", autogroup.grouping_distance
          print "autogroup parts to group: ", autogroup.parts_to_group
        if self.hocr:
          self.page = HocrPager(self.img, hocr=self.hocr, classify_ccs=autogroup)
        elif self.mode == "teubnerappcrit":
           self.page = AppCritTeubner(self.img, classify_ccs=autogroup)
        elif self.mode == "teubnerbody":
           self.page = BodyTeubner(self.img, classify_ccs=autogroup)
        else:
          self.page = SinglePage(self.img, classify_ccs=autogroup)
      else:#not autogrouped
        if self.hocr:
          self.page = HocrPager(self.img, hocr=self.hocr)
        else:
          self.page = SinglePage(self.img)
      self.page.segment()
      if self.debug:
         t = time.time() - t
         print "\t segmentation done [",t,"sec]"


      
   def save_debug_images(self, imageBase):
      """Saves the following images to the current working directory:

  **debug_lines.png**
    Has a frame drawn around each detected line.

  **debug_chars.png**
    Has a frame drawn around each detected character.

  **debug_words.png**
    Has a frame drawn around each detected word.
"""
      rgbfilename = imageBase + "_debug_lines.png"
      rgb = self.page.show_lines()
      rgb.save_PNG(rgbfilename)
      print "file '%s' written" % rgbfilename
      rgbfilename = imageBase + "_debug_chars.png"
      rgb = self.page.show_glyphs()
      rgb.save_PNG(rgbfilename)
      print "file '%s' written" % rgbfilename
      rgbfilename = imageBase + "_debug_words.png"
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
         self.output = self.output + self.correct_common_errors(t[0])
         if not (t[0] == u'\n'):
            self.output = self.output + " "
      #self.output = self.correct_common_errors(self.output)
      #self.output = self._normalize(self.output) 

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

   def correct_common_errors(self,unicode_input):
      import re
      import unicodedata
      left_single_quote = unicode(u"\N{LEFT SINGLE QUOTATION MARK}")
      right_single_quote = unicode(u"\N{RIGHT SINGLE QUOTATION MARK}")
      smooth_breathing = unicode(u"\N{COMBINING COMMA ABOVE}")
      rough_breathing = unicode(u"\N{COMBINING REVERSED COMMA ABOVE}")
      circumflex = unicode(u"\N{COMBINING GREEK PERISPOMENI}")
      acute_accent = unicode(u"\N{COMBINING ACUTE ACCENT}")
      grave_accent = unicode(u"\N{COMBINING GRAVE ACCENT}")
      apostrophe = unicode(u"\N{APOSTROPHE}")
      middle_dot = unicode(u"\N{MIDDLE DOT}")
      vowels =  unicode(u"\N{GREEK SMALL LETTER ALPHA}\N{GREEK SMALL LETTER EPSILON}\N{GREEK SMALL LETTER ETA}\N{GREEK SMALL LETTER IOTA}\N{GREEK SMALL LETTER OMICRON}\N{GREEK SMALL LETTER UPSILON}\N{GREEK SMALL LETTER OMEGA}")
      capital_vowels =  unicode(u"\N{GREEK CAPITAL LETTER ALPHA}\N{GREEK CAPITAL LETTER EPSILON}\N{GREEK CAPITAL LETTER ETA}\N{GREEK CAPITAL LETTER IOTA}\N{GREEK CAPITAL LETTER OMICRON}\N{GREEK CAPITAL LETTER UPSILON}\N{GREEK CAPITAL LETTER OMEGA}")
      consonants =  unicode(u"\N{GREEK SMALL LETTER BETA}\N{GREEK SMALL LETTER DELTA}\N{GREEK SMALL LETTER ZETA}\N{GREEK SMALL LETTER THETA}\N{GREEK SMALL LETTER KAPPA}\N{GREEK SMALL LETTER LAMDA}\N{GREEK SMALL LETTER MU}\N{GREEK SMALL LETTER NU}\N{GREEK SMALL LETTER XI}\N{GREEK SMALL LETTER PI}\N{GREEK SMALL LETTER RHO}\N{GREEK SMALL LETTER SIGMA}\N{GREEK SMALL LETTER TAU}\N{GREEK SMALL LETTER PHI}\N{GREEK SMALL LETTER CHI}\N{GREEK SMALL LETTER PSI}")
      capital_rho = unicode(u"\N{GREEK CAPITAL LETTER RHO}")
      caps_with_breathing = capital_vowels + capital_rho
      #These try to produce canonical ordering of accents and breathing
      #this regex reorders breathing + accent to accent + breathing
      unicode_input = unicodedata.normalize('NFD',unicode_input)
      out = re.sub(ur'(['+smooth_breathing+rough_breathing + ur'])([' + acute_accent + grave_accent + ur'])',r'\2' + r'\1',unicode_input)
      #this regex reorders circumflex + breathing to breathing + circumflex
      out = re.sub(ur'([' + circumflex +  ur'])([' +smooth_breathing+rough_breathing + ur'])',r'\2' + r'\1',out)

      #These try to fix common identification errors and ambiguities.
      #They are gradually being replaced by positional analysis
      
      #this regex takes the sequence vowel+consonant+acute accent and 
      #arranges it as vowel+accent+consonant
      #certain consonants tend to 'steal' the acute
      #out = re.sub(ur'(.*[' + vowels + ur'])([' + consonants + ur'])' + acute_accent,r'\1'+acute_accent+r'\2',out)
     
      #replace vowel + left_single_quote with vowel and acute accent. 
      
      # A left single quote should appear at the beginning of a word only, so this is ok.
      out = re.sub(ur'(.*[' + vowels + ur'])(' + left_single_quote + ur')' ,r'\1'+rough_breathing,out)

      out = re.sub(left_single_quote + ur'([' + caps_with_breathing + ur'])',r'\1' + rough_breathing,out)
      out = re.sub(apostrophe + ur'([' + capital_vowels + ur'])',r'\1' + smooth_breathing,out)
      #out = re.sub(ur'(.*[' + vowels + ur'])(' + right_single_quote + ur')' ,r'\1'+rough_breathing,out)
      #print "outpu: " + out.encode('utf-8')

      # full.stop or middle.dot plus apostrophe -> full.stop or middle.dot plus right.single.quotation.mark
      out = re.sub(ur"([\." + middle_dot + ur"])'",ur'\1' + right_single_quote,out)

      #replace double grave accent with grave accent and smooth breathing
      out = re.sub(grave_accent + grave_accent, grave_accent + smooth_breathing, out)

      #These are byproducts of the agressive semi-colon and colon searching. Remove when you figure out how to
      #remove the comma and full.stop
      out = out.replace(';,', ';')
      out = out.replace(':.' , ':')
      out = out.replace(',;', ';')
      out = out.replace('.:',':')
       
      #No longer necessary due to positional analysis
      #this regex replaces final combining commas (i.e. 'smooth breathing') 
      #with apostrophes, if they appear after a consonant
      #print "input: " + out.encode('utf-8')
      #out = re.sub(ur'([' + consonants + ur'])' + smooth_breathing,r'\1' + apostrophe,out)

      #No longer necessary due to positional analysis
      #this regex replaces vowel + apostrophe + letter with vowel + acute + letter
      #out = re.sub(ur'([' + vowels + ur'])' + apostrophe + ur'([' + vowels + consonants + ur'])' ,r'\1' + smooth_breathing + r'\2',out)

      #No longer necessary, due to positional analysis. However, we might decide to operate this on apostrophes
      #this regex replaces (full.stop + smooth_breathing + end of word) with full.stop + right.single.quote
      #out = re.sub(ur'\.' + smooth_breathing ,r".'",out)
      #print "output: " + out.encode('utf-8')
      return out

   def store_hocr(self,page_path,hocr_tree):
      import lxml
      from lxml import etree
      import string
      x = 0 
      root = hocr_tree.getroot()
      body = root.find("{http://www.w3.org/1999/xhtml}body")
      pageDiv = etree.SubElement(body,"{http://www.w3.org/1999/xhtml}div")
      pageDiv.set("class","ocr_page")
      page_path = page_path.translate(None,'/')#strip out slashes, which aren't allowed on ids
      pageDiv.set("id",page_path)
      for line in self.page.textlines:
         lineSpan = etree.SubElement(pageDiv,"{http://www.w3.org/1999/xhtml}span")
         lineSpan.set("class","ocr_line")
         titleText = "bbox " + str(line.bbox.ul_x) + " " + str(line.bbox.ul_y) + " " + str(line.bbox.lr_x) + " " + str(line.bbox.lr_y)
         lineSpan.set("title", titleText)
         word_tuples=line.to_word_tuples()
         for t in word_tuples:
            if not (t[0] == u'\n'):
               word_unicode = unicode(t[0])
               word_unicode = self.correct_common_errors(word_unicode)
               wordSpan = etree.SubElement(lineSpan,"{http://www.w3.org/1999/xhtml}span")
               wordSpan.set("class","ocr_word")
               word_ul_x_glyph =  min(t[1], key=lambda glyph: glyph.ul_x)
               word_ul_y_glyph =  min(t[1], key=lambda glyph: glyph.ul_y)
               word_lr_x_glyph =  max(t[1], key=lambda glyph: glyph.lr_x)
               word_lr_y_glyph =  max(t[1], key=lambda glyph: glyph.lr_y)
               titleText = "bbox " + str(word_ul_x_glyph.ul_x) + " " + str(word_ul_y_glyph.ul_y) + " " + str(word_lr_x_glyph.lr_x) + " " + str(word_lr_y_glyph.lr_y)
               wordSpan.set("title", titleText)
               wordSpan.text = word_unicode
               wordSpan.tail = " "
               x = x + 1
         brElement = etree.SubElement(pageDiv,"{http://www.w3.org/1999/xhtml}br")

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
         print "Doing page Segmentation..."
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
      
   def save_text_hocr(self, tree, filename):
      import lxml
      from lxml import etree  
      f = codecs.open(filename, "w")
      f.write(etree.tostring(tree, encoding='utf-8'))
      f.close()

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


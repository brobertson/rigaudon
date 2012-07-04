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



from gamera.core import * 
from gamera.plugins.pagesegmentation import textline_reading_order
from gamera.toolkits.ocr.ocr_toolkit import *
from gamera.toolkits.ocr.classes import Textline,Page,ClassifyCCs
import gamera.kdtree as kdtree
import unicodedata
import sys



class WholisticPage(Page):
   def __init__(self, img):
      self.img = img
      #cknn = knn.kNNInteractive([], ["aspect_ratio", "volume64regions", "moments", "nholes_extended"], 0)
      #cknn.from_xml_filename("x01/classifier-all-2/classifier_glyphs.xml")
      #if(opt.ccsfilter):
      #   the_ccs = ccs
      #else:
      the_ccs = img.cc_analysis()
      self.median_cc = int(median([cc.nrows for cc in the_ccs]))
      #autogroup = ClassifyCCs(cknn)
      #autogroup.parts_to_group = 3
      #autogroup.grouping_distance = max([2,median_cc / 8])
      Page.__init__(self, img)#, classify_ccs=autogroup)
      
      #print "autogrouping glyphs activated."
      #print "maximal autogroup distance:", autogroup.grouping_distance

   def lines_to_chars(self):
      self.textlines = self.get_line_glyphs(self.img, self.ccs_lines)



   def check_glyph_greek_accent(self, item,glyph):
      remove = []
      add = []
      result = []
      if((glyph.ul_x == item.ul_x and glyph.ul_y == item.ul_y and glyph.lr_x == item.lr_x and glyph.lr_y == item.lr_y) or \
            glyph.intersects_x(item) or \
            (glyph.distance_bb(item) < 3 and \
               (glyph.distance_cx(item) < (self.median_cc / 2) or 2*glyph.nrows < item.nrows or 2*item.nrows < glyph.nrows ) \
            )\
         ): ##nebeinander?
         #  print "y"
         remove.append(glyph)
         remove.append(item)
         new = union_images([item,glyph])
         add.append(new)
      result.append(add)      #result[0] == ADD
      result.append(remove)      #result[1] == REMOVE
      return result





   def get_line_glyphs(self,image,textlines):
      i=0
      show = []
      lines = []
      ret,sub_ccs = image.sub_cc_analysis(textlines)
      #print "doc has %d lines" % len(sub_ccs)
      linenumber = 0
      for ccs in sub_ccs:
         linenumber = linenumber + 1
         #print "line %d" % linenumber
         line_bbox = Rect(textlines[i])
         i = i + 1
         glyphs = ccs[:]
         newlist = []

         remove = []
         add = []
         result = []
         glyphs.sort(lambda x,y: cmp(x.ul_x, y.ul_x))
         #print "first run"
         for position, item in enumerate(glyphs):
            olditem = item
            left = max(0,position - 5)
            right = min(position + 5, len(glyphs))
            
            checklist = glyphs[left:right]

            for glyph in checklist:
               if(item == glyph):
                  continue

               result = self.check_glyph_greek_accent(item,glyph)
               if(len(result[0]) > 0):  #something has been joind...
                  item = result[0][0]
                  #add.append(result[0][0])   #joind glyph
                  remove.append(result[1][0])        #first part of joind one
                  remove.append(result[1][1])        #second part of joind one
                  
               
            if olditem != item:
               add.append(item)
               
            for elem in remove:
               if(elem in glyphs):
                  glyphs.remove(elem)

         for elem in add:
            glyphs.append(elem)

         remove = []
         add = []
         glyphs = textline_reading_order(glyphs)
         
         
       
         glyphs = list(set(glyphs))
         #print len(glyphs)
         new_line = WholisticTextline(line_bbox)
         final = []
         if(len(glyphs) > 0):
           for glyph in glyphs:
            final.append(glyph)

         new_line.add_glyphs(final,False)
         #new_line.sort_glyphs()  #reading order -- from left to right
         lines.append(new_line)

         for glyph in glyphs:
           show.append(glyph)

      return lines
            








class WholisticTextline(Textline):
   #called after classification
   def sort_glyphs(self):
      
      self.glyphs = textline_reading_order(self.glyphs)
      
      
      #begin calculating threshold for word-spacing
      spacelist = []
      for i in range(len(self.glyphs) - 1):
         spacelist.append(self.glyphs[i + 1].ul_x - self.glyphs[i].lr_x)
      if(len(spacelist) > 0):
         threshold = median(spacelist)
         threshold = threshold * 2.0
      else:
         threshold  = 0
      #end calculatin threshold for word-spacing
      
      self.words = chars_make_words(self.glyphs, threshold)
      
   
   
   def to_string(self):
      k = 3
      max_k = 10
      output = u""
      for word in self.words:
         characters = []
         skipids = ["manual.xi.upper", "manual.xi.lower", "manual.theta.outer"]
         for glyph in word:
            mainid = glyph.get_main_id()
            
            if mainid == "comma" or mainid == "combining.comma.above":
               #print "%s - center_y: %d - med_center: %d" % (mainid, glyph.center.y, med_center)
               if glyph.center.y > self.bbox.center.y:
                  glyph.classify_automatic("comma")
               else:
                  glyph.classify_automatic("combining.comma.above")
            
            mainid = glyph.get_main_id()
            
            mainid = mainid.split(".and.")
            for a in mainid:
               
                  
               char = return_char(a)
               #print "added %s to output" % char
               output = output + char#unicodedata.normalize('NFD', char)
            
         output = output + " "
      
      return output


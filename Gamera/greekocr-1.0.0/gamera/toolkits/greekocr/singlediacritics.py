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

class SinglePage(Page):      
   def lines_to_chars(self):
      #import pprint 
      #print "inside linestochars"
      #pp = pprint.PrettyPrinter(indent=4, depth=4)
      #print "cc_lines:"
      #print pp.pprint(self.ccs_lines)
      subccs = self.img.sub_cc_analysis(self.ccs_lines)
      #print "subccs:"
      #print pp.pprint(subccs) 
      for i,segment in enumerate(self.ccs_lines):
         self.textlines.append(SingleTextline(segment, subccs[1][i]))
      #print "textlines"
      #pp.pprint(self.textlines)


class Character(object):
   def __init__(self, glyph):
      self.maincharacter = glyph
      self.unicodename = glyph.get_main_id()
      self.unicodename = self.unicodename.replace(".", " ").upper()
      #print self.unicodename
      #self.unicodename = 
      self.combinedwith = []
      #print self.maincharacter
      
   def addCombiningDiacritics(self, diacrit):
      self.combinedwith.append(diacrit)
      pass
   
   def toUnicodeString(self):
      try:
         str = u""
         mainids = self.maincharacter.get_main_id().split(".and.")
         for char in mainids:
            if char == "skip" or char == "unclassified":
               continue
            str = str + u"%c" % return_char(char)
               
         #str = u"" + return_char(self.unicodename)
         for char in self.combinedwith:
            #char = char.get_main_id().replace(".", " ").upper()
            mainids = char.get_main_id().split(".and.")
            #print mainids
            for char in mainids:
               if char == "skip":
                  continue
               #print "added %s to output" % char
               str = str + u"%c" % return_char(char)
      
         return unicodedata.normalize('NFD', str)
      except:
         #print self.unicodename
         return u"E"
         
      
      
class SingleTextline(Textline):
   def sort_glyphs(self):
      self.glyphs.sort(lambda x,y: cmp(x.ul_x, y.ul_x))
      #begin calculating threshold for word-spacing
      glyphs = []
      printing_glyphs = []
      for g in self.glyphs:
         # print g.id_name, g.ul_x, self.is_small_glyph(g)
         if self.is_combining_glyph(g) or self.is_small_glyph(g):
            continue
         # print g.id_name, g.ul_x
         glyphs.append(g)
      for g in self.glyphs:
         # print g.id_name, g.ul_x, self.is_small_glyph(g)
         if self.is_skip(g):
            continue
         # print g.id_name, g.ul_x
         printing_glyphs.append(g) 
  
      spacelist = []
      total_space = 0
      for i in range(len(glyphs) - 1):
         #print "between ", glyphs[i].id_name, " and ", glyphs[i+1].id_name, (glyphs[i + 1].ul_x - glyphs[i].lr_x)
         spacelist.append(glyphs[i + 1].ul_x - glyphs[i].lr_x)
      if(len(spacelist) > 0):
         threshold = median(spacelist)
         #print "threshold: ", threshold
         threshold = threshold * 3
      else:
         threshold  = 0
      #end calculating threshold for word-spacing
      

      wordlist=[]
      word = []
      previousNonCombining = None
      currentNonCombining = None
      for i in range(len(printing_glyphs)):   
            if not self.is_combining_glyph(printing_glyphs[i]): 
              previousNonCombining = currentNonCombining
              #print "PNC now: ",
             # if previousNonCombining:
               # print previousNonCombining.id_name
             # else:
                #print "NONE"
              currentNonCombining = printing_glyphs[i]
              #print "CNC now: ", currentNonCombining.id_name
              if(previousNonCombining and currentNonCombining and ((currentNonCombining.ul_x - previousNonCombining.lr_x) > threshold)):
               #   print "space: ", previousNonCombining.id_name, " and ", currentNonCombining.id_name, " : ", (currentNonCombining.ul_x - previousNonCombining.lr_x), " over ", threshold
                  wordlist.append(word)
                  word = []
            word.append(printing_glyphs[i])
      if(len(word) > 0):
         wordlist.append(word)
      self.words= wordlist



   def is_combining_glyph(self, glyph):
      #must both have word 'combining', and not have word 'letter'
      # the latter to avoid grouped things, like 
      #greek.small.letter.eta.and.combining.acute.accent
      #which could get treated as combining, alas, forcing a
      #space on the output
      ret =  (glyph.get_main_id().find("combining") != -1) and (glyph.get_main_id().find("letter") == -1)
      return ret
   def is_joined_glyph(self, glyph):
      ret = glyph.get_main_id().find(".and.") != -1
      return ret
   def includes_letter(self,glyph):
      ret = glyph.get_main_id().find("letter") != -1
      return ret
   def is_skip(self, glyph):
      ret = glyph.get_main_id().find("skip") != -1
      return ret
   def is_small_glyph(self, glyph): 
      myId = glyph.get_main_id()
      for string in ["skip","SKIP","comma","middle.dot","apostrophe","full.stop","_split"]:
         if myId.find(string) > -1: 
            return 1
      return 0

   def to_word_tuples(self):
      k = 3
      max_k = 10
      output = []
      for word in self.words:
         med_center = median([g.center.y for g in word])
         glyphs_combining = []
         characters = []
         nodes_normal = []
         skipids = ["manual.xi.upper", "manual.xi.lower", "manual.theta.outer", "_split.splitx", "skip"]
         for glyph in word:
            mainid = glyph.get_main_id()
            
            if skipids.count(mainid) > 0:
               continue
            elif mainid == "manual.xi.middle":
               glyph.classify_automatic("greek.capital.letter.xi")
            elif mainid == "manual.theta.inner":
               glyph.classify_automatic("greek.capital.letter.theta")
            elif mainid == "comma" or mainid == "combining.comma.above":
               #print "%s - center_y: %d - med_center: %d" % (mainid, glyph.center.y, med_center)
               if glyph.center.y > self.bbox.center.y:
                  glyph.classify_automatic("comma")
               else:
                  glyph.classify_automatic("combining.comma.above")
            elif mainid == "full.stop" or mainid == "middle.dot":
               if glyph.center.y > self.bbox.center.y:
                  glyph.classify_automatic("full.stop")
               else:
                  glyph.classify_automatic("middle.dot")
            elif mainid == "combining.greek.ypogegrammeni":
               if glyph.center.y < self.bbox.center.y:
                  glyph.classify_automatic("combining.acute.accent")
            elif mainid == "right.single.quotation.mark":
               if glyph.center.y > self.bbox.center.y:
                  #too low to be a quotation mark, must be a comma
                  glyph.classify_automatic("comma")
            elif mainid.find("manual") != -1 or mainid.find("split") != -1:
               continue
            
            if self.is_combining_glyph(glyph) and not(self.is_joined_glyph(glyph) and self.includes_letter(glyph)):# avoid corner case where we have a glyph that is 'greek.small.letter.eta.and.combining.acute'
               glyphs_combining.append(glyph)
            else:
               c = Character(glyph)
               characters.append(c)
               #print c
               nodes_normal.append(kdtree.KdNode((glyph.center.x, glyph.center.y), c))
         
         if (nodes_normal == None or len(nodes_normal) == 0):
            continue
            
         tree = kdtree.KdTree(nodes_normal)
         
         for g in glyphs_combining:
            fast = True
            if fast:
               knn = tree.k_nearest_neighbors((g.center.x, g.center.y), k)
               knn[0].data.addCombiningDiacritics(g)
            else:
               found = False
               while (not found) and k < max_k:
                  knn = tree.k_nearest_neighbors((g.center.x, g.center.y), k)
                  
                  for nn in knn:
                     if (nn.data.maincharacter.get_main_id().split(".").count("greek") > 0) and not found:
                        nn.data.addCombiningDiacritics(g)
                        found = True
                        break
               
                  k = k + 2      
                  
         wordString = ""      
         for c in characters:
            #output = output + c.toUnicodeString()
            wordString = wordString + c.toUnicodeString()
         #output = output + wordString + " "
         output.append((wordString,word))
      return output

   def to_string(self):
     
      tuples = self.to_word_tuples()
      stringOut = ""
      x = 0
      for t in tuples:
         stringOut = stringOut + t[0] + " "

        # print foo, bar

      return stringOut  


   


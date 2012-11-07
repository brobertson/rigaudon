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
      
   # Implement a simple vertical ordering
   def order_lines(self):
      self.ccs_lines.sort(lambda s,t: s.offset_y - t.offset_y)
   def page_to_lines(self):
      self.ccs_lines = self.img.bbox_mcmillan(None,1,0.5,10,5)
class ImageSegmentationError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
               
class FindAppCritTeubner(SinglePage):
	def page_to_lines(self):
		#this subdivides app. crit. in teubners
		
		#this cuts up app. crit into lines
		#self.ccs_lines = self.img.projection_cutting(Tx=25, Ty=8, noise=3)	
		#self.ccs_lines = self.img.projection_cutting(Tx=2000, Ty=5, noise=15)
		self.ccs_lines = self.img.bbox_merging(Ey=8)#this finds app. crit
		
		#word-by-word body of teubner
		#self.ccs_lines = self.img.bbox_merging(Ex=15,Ey=5)
		#self.ccs_lines = self.img.bbox_mcmillan(None,1,1,20,5)

class AppCritTeubner(SinglePage):
	def page_to_lines(self):
		#this cuts up app. crit into lines
		#self.ccs_lines = self.img.projection_cutting(Tx=1700, Ty=1, noise=50)
	   #self.ccs_lines = self.img.bbox_mcmillan(None,1,.2,10,5)
	   self.ccs_lines = self.img.bbox_merging(Ex=2,Ey=.5)
	   
class BodyTeubner(SinglePage):
	def page_to_lines(self):
		#word-by-word body of teubner
		#self.ccs_lines = self.img.bbox_merging(Ex=30,Ey=2)               
      #self.ccs_lines = self.img.bbox_mcmillan(None,1,.2,10,5)
      self.ccs_lines = self.img.bbox_merging(Ex=10,Ey=4)#finds boxes for each word

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
   def identify_ambiguous_glyphs(self):
      print
      for g in self.glyphs:
         mainid = g.get_main_id()
         if mainid == "comma" or mainid == "combining.comma.above":
            #print "%s - center_y: %d - med_center: %d" % (mainid, glyph.center.y, med_center)
            if g.center.y > self.bbox.center.y:
               g.classify_automatic("comma")
            else:
               g.classify_automatic("combining.comma.above")
         elif mainid == "apostrophe":
            if g.center.y > self.bbox.center.y:
               g.classify_automatic("comma")
         elif mainid == "full.stop" or mainid == "middle.dot":
            if g.center.y > self.bbox.center.y:
               g.classify_automatic("full.stop")
            else:
               g.classify_automatic("middle.dot")
         elif mainid == "combining.greek.ypogegrammeni":
            if g.center.y < self.bbox.center.y:
               g.classify_automatic("combining.acute.accent")
         elif mainid == "combining.acute.accent":
            if g.center.y > self.bbox.center.y:
               g.classify_automatic("combining.greek.ypogegrammeni")
         elif mainid == "right.single.quotation.mark":
            if g.center.y > self.bbox.center.y:
               #too low to be a quotation mark, must be a comma
               g.classify_automatic("comma")
         if g.get_main_id() == "apostrophe" or g.get_main_id() == 'right.single.quotation.mark' or g.get_main_id() == 'combining.comma.above':
            glyph_cl_x = (g.ul_x + (g.lr_x - g.ul_x)/2)
            glyph_cl_y = (g.ul_y + (g.lr_y - g.ul_y)/2)
##            print g.get_main_id(), " at: ", glyph_cl_x, glyph_cl_y
            for other in self.glyphs:
               if self.is_greek_small_letter(other):
                 # print "other candidate:", other.get_main_id()
                  other_cl_y = (other.ul_y + (other.lr_y - other.ul_y)/2)
                  #print "at ", other.ul_x, other.lr_x, other_cl_y
                  if (glyph_cl_x > other.ul_x) and (glyph_cl_x < other.lr_x) and (glyph_cl_y < other_cl_y):#there is a character inside whose width the 'apostrophe's center line lies
##                     print "there is something below:", other.id_name
                     g.classify_automatic("combining.comma.above")
                     break
            #there are no other glyphs underneith; a for's else runs with no break
            else:
##               print "nothing underneith"
               g.classify_automatic("apostrophe")#it could be a right.single.quotation.mark, however
               #we have no way of telling
         
         if g.get_main_id() == 'left.single.quotation.mark' or g.get_main_id() == 'combining.reversed.comma.above':
            glyph_cl_x = (g.ul_x + (g.lr_x - g.ul_x)/2)
            glyph_cl_y = (g.ul_y + (g.lr_y - g.ul_y)/2)
##            print g.get_main_id(), " at: ", glyph_cl_x, glyph_cl_y
            for other in self.glyphs:
               if self.is_greek_small_letter(other):
                 # print "other candidate:", other.get_main_id()
                  other_cl_y = (other.ul_y + (other.lr_y - other.ul_y)/2)
                  #print "at ", other.ul_x, other.lr_x, other_cl_y
                  if (glyph_cl_x > other.ul_x) and (glyph_cl_x < other.lr_x) and (glyph_cl_y < other_cl_y):#there is a character inside whose width the 'apostrophe's center line lies
##                     print "there is something below:", other.id_name
                     g.classify_automatic("combining.reversed.comma.above")
                     break
            #there are no other glyphs underneith; a for's else runs with no break
            else:
##               print "nothing underneith"
               g.classify_automatic("left.single.quotation.mark")#it could be a right.single.quotation.mark, however
               #we have no way of telling
   def sort_glyphs(self):
      self.glyphs.sort(lambda x,y: cmp(x.ul_x, y.ul_x))
      self.identify_ambiguous_glyphs()
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
      #scan for breathing + (accent) + capital letter
      glyphs_out = []
      reordered_glyphs = []
      just_reordered = False
##      print "printing glyphs before cap. reordering:"
     
      for glyph in printing_glyphs:
#         if self.is_greek_capital_letter(glyph) and len(glyphs_out):
#            print "Cap:" 
#            print glyph.id_name
#            print glyphs_out[-1].id_name
         greek_capital_vowels = ['greek.capital.letter.alpha','greek.capital.letter.epsilon','greek.capital.letter.eta','greek.capital.letter.iota','greek.capital.letter.omicron','greek.capital.letter.upsilon','greek.capital.letter.omega']
         greek_capital_rho=['greek.capital.letter.rho']
         can_combine_with_rough_breathing = greek_capital_vowels + greek_capital_rho
         #if just_reordered == False and len(glyphs_out) > 0 and self.is_greek_capital_letter(glyph) and self.is_combining_glyph(glyphs_out[-1]):#and the previous accent isn't too far away...
         if just_reordered == False and len(glyphs_out) > 0  and self.is_combining_glyph(glyphs_out[-1]) and (glyph.get_main_id() in can_combine_with_rough_breathing) and not (glyph.get_main_id() in greek_capital_rho and not (glyphs_out[-1] == 'combining.reversed.comma.above')):#and the previous accent isn't too far away...
         
            print "Reorder cap?"
            capital_char_width = (glyph.lr_x - glyph.ul_x)
            if self.is_combining_glyph(glyphs_out[-1]):#if the 'combining glyph' already on the stack is actually two-in-one, then we need to
                                                       #give a bit more room.
               max_distance = capital_char_width
            else:
               max_distance = capital_char_width / 2
            print "width: ", capital_char_width
            distance_to_accent = (glyph.ul_x - glyphs_out[-1].ul_x)
            print "between ", glyph.id_name, " and ", glyphs_out[-1].id_name, distance_to_accent
            reordered_glyphs = []
            reordered_glyphs.append(glyph)
            if distance_to_accent < max_distance:
               just_reordered = True
               reordered_glyphs.append(glyphs_out[-1])
               glyphs_out = glyphs_out[:-1] #strip the last glyph off of this stack
               print "reordered " + glyph.get_main_id()
               if len(glyphs_out) > 0 and self.is_combining_glyph(glyphs_out[-1]):#and it isn't too far away
                  distance_to_accent = (glyph.ul_x - glyphs_out[-1].ul_x)
                  print "possibly two accents"
                  print "between ", glyph.id_name, " and ", glyphs_out[-1].id_name, distance_to_accent
                  if distance_to_accent < max_distance:
                     reordered_glyphs.append(glyphs_out[-1])
                     glyphs_out = glyphs_out[:-1]
            glyphs_out = glyphs_out + reordered_glyphs
         else:
            glyphs_out.append(glyph)
            just_reordered = False
      printing_glyphs = glyphs_out
      print "printing glyphs after cap. reordering:"
      for glyph in printing_glyphs:
         print glyph.get_main_id()
      spacelist = []
      total_space = 0
      for i in range(len(glyphs) - 1):
         #print "between ", glyphs[i].id_name, " and ", glyphs[i+1].id_name, (glyphs[i + 1].ul_x - glyphs[i].lr_x)
         spacelist.append(glyphs[i + 1].ul_x - glyphs[i].lr_x)
      if(len(spacelist) > 0):
         threshold = median(spacelist)
         #print "threshold: ", threshold
         threshold = threshold * 2.7#Meineke, Kaibel: 3
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
                  #print "space: ", previousNonCombining.id_name, " and ", currentNonCombining.id_name, " : ", (currentNonCombining.ul_x - previousNonCombining.lr_x), " over ", threshold
                  wordlist.append(word)
                  word = []
            word.append(printing_glyphs[i])
      if(len(word) > 0):
         wordlist.append(word)
      self.words= wordlist
      print "SELF WORDS:"
      for word in self.words:
         for g in word:
            print g.get_main_id()
         print


   def is_greek_capital_letter(self, glyph):
      return (glyph.get_main_id().find("greek") != -1) and (glyph.get_main_id().find("capital") != -1) and (glyph.get_main_id().find("letter") != -1)
   def is_greek_small_letter(self, glyph):
      return (glyph.get_main_id().find("greek") != -1) and (glyph.get_main_id().find("small") != -1) and (glyph.get_main_id().find("letter") != -1)   
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
               print
               print "KNN!"
               for aKnn in knn:
                  print aKnn.data.unicodename
                  #It isn't just whose center is closer, but also, who is below
                  if (aKnn.data.maincharacter.ul_x < g.center.x) and (aKnn.data.maincharacter.lr_x > g.center.x):
                     aKnn.data.addCombiningDiacritics(g)
                     print "this is determined to be below"
                     break
               else:
                  search_x_point = 0
                  if (g.get_main_id() == 'combining.grave.accent'):
                     search_x_point = g.lr_x
                  elif (g.get_main_id() == 'combining.acute.accent'):
                     search_x_point = g.ul_x
                  else:
                     print "I give up: no NN below??"
                     knn[0].data.addCombiningDiacritics(g)
                     break
                  for aKnn in knn:
                     if (aKnn.data.maincharacter.ul_x < search_x_point) and (aKnn.data.maincharacter.lr_x > search_x_point):
                        aKnn.data.addCombiningDiacritics(g)
                        print "found on edge of", aKnn.data.unicodename
                        break
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


   


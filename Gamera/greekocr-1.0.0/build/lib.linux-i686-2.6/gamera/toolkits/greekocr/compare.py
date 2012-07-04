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

import unicodedata
import codecs

def levenshtein(s1, s2):
   """Computes the Levenshtein distance (aka edit distance) between
the two Unicode strings *s1* and *s2*. Signature:

  ``levenshtein(s1, s2)``

This implementation differs from the plugin *edit_distance* in the Gamera
core in two points:

 - the Gamera core function is implemented in C++ and currently only
   works with ASCII strings

 - this implementation is written in pure Python and therefore somewhat
   slower, but it works with Unicode strings.

For details about the algorithm see
http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance
"""
   if len(s1) < len(s2):
      return levenshtein(s2, s1)
   if not s1:
      return len(s2)
 
   previous_row = xrange(len(s2) + 1)
   for i, c1 in enumerate(s1):
      current_row = [i + 1]
      for j, c2 in enumerate(s2):
         insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
         deletions = current_row[j] + 1       # than s2
         substitutions = previous_row[j] + (c1 != c2)
         current_row.append(min(insertions, deletions, substitutions))
      previous_row = current_row
   return previous_row[-1]
 


def levenshtein_multi_unicode(str1, str2):
   #remove linebreaks
   str1 = str1.replace("\n", "")
   str2 = str2.replace("\n", "")
   
   #remove spaces
   str1 = str1.replace(" ", "")
   str2 = str2.replace(" ", "")

   str1_n = unicodedata.normalize("NFD", str1)
   str2_n = unicodedata.normalize("NFD", str2)
   
   return levenshtein(str1_n, str2_n), len(str1_n), len(str2_n)



def errorrate(groundtruth, ocr):
   """For the two given Unicode strings, the edit distance divided by the
length of the first string is returned.
Signature:

  ``errorrate(groundtruth, ocr)``

"""
   errorcount, gtlength, ocrlength = levenshtein_multi_unicode(groundtruth, ocr)
   rate = float(errorcount) / gtlength
   print "Errorcount:          %d" % errorcount
   print "Characters in GT:    %d" % gtlength
   print "Characters in OCR:   %d" % ocrlength
   print "Error Rate:          %.2f %%" % (rate * 100)
   #print "=%5d %5d %5d %3.2f" % (errorcount, gtlength, ocrlength, rate*100)
   
   return rate


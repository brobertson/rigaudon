#encoding: utf-8
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

import sys

charactermap = {
   "GREEK CAPITAL LETTER ALPHA": "A","GREEK CAPITAL LETTER BETA": "B",
   "GREEK CAPITAL LETTER GAMMA": "G","GREEK CAPITAL LETTER DELTA": "D",
   "GREEK CAPITAL LETTER EPSILON": "E","GREEK CAPITAL LETTER ZETA": "Z",
   "GREEK CAPITAL LETTER ETA": "H","GREEK CAPITAL LETTER THETA": "J",
   "GREEK CAPITAL LETTER IOTA": "I","GREEK CAPITAL LETTER KAPPA": "K",
   "GREEK CAPITAL LETTER LAMDA": "L","GREEK CAPITAL LETTER MU": "M",
   "GREEK CAPITAL LETTER NU": "N","GREEK CAPITAL LETTER XI": "X",
   "GREEK CAPITAL LETTER OMICRON": "O","GREEK CAPITAL LETTER PI": "P",
   "GREEK CAPITAL LETTER RHO": "R","GREEK CAPITAL LETTER SIGMA": "C",
   "GREEK CAPITAL LETTER TAU": "T","GREEK CAPITAL LETTER UPSILON": "U",
   "GREEK CAPITAL LETTER PHI": "F","GREEK CAPITAL LETTER CHI": "Q",
   "GREEK CAPITAL LETTER PSI": "Y","GREEK CAPITAL LETTER OMEGA": "W",
   "GREEK SMALL LETTER ALPHA": "a","GREEK SMALL LETTER BETA": "b",
   "GREEK SMALL LETTER GAMMA": "g","GREEK SMALL LETTER DELTA": "d",
   "GREEK SMALL LETTER EPSILON": "e","GREEK SMALL LETTER ZETA": "z",
   "GREEK SMALL LETTER ETA": "h","GREEK SMALL LETTER THETA": "j","GREEK THETA SYMBOL": "j",
   "GREEK SMALL LETTER IOTA": "i","GREEK SMALL LETTER KAPPA": "k",
   "GREEK SMALL LETTER LAMDA": "l","GREEK SMALL LETTER MU": "m",
   "GREEK SMALL LETTER NU": "n","GREEK SMALL LETTER XI": "x",
   "GREEK SMALL LETTER OMICRON": "o","GREEK SMALL LETTER PI": "p",
   "GREEK SMALL LETTER RHO": "r","GREEK SMALL LETTER FINAL SIGMA": "c",
   "GREEK SMALL LETTER SIGMA": "s","GREEK SMALL LETTER TAU": "t",
   "GREEK SMALL LETTER UPSILON": "u","GREEK SMALL LETTER PHI": "f",
   "GREEK SMALL LETTER CHI": "q","GREEK SMALL LETTER PSI": "y",
   "GREEK SMALL LETTER OMEGA": "w", "SPACE": " ", 
   "FULL STOP": ".", "COMMA": ",", "HYPHEN-MINUS": "-"
}

accentmap = [
   ['\\`%c', ['combining.grave.accent']], 
   ['\\\'%c', ['combining.acute.accent']], 
   ['\\~%c', ['combining.greek.perispomeni']], 
   ['\\"%c', ['combining.diaresis']], 
   ['\\u{%c}', ['combining.breve']], 
   ['\\U{%c%c}', ['combining.double.breve']], 
   ['\\=%c', ['combining.overline']], 
   ['\\r{%c}', ['combining.comma.above']], 
   ['\\s{%c}', ['combining.reversed.comma.above']], 
   ['\\Ad{%c}', ['combining.acute.accent', 'combining.diaresis']], 
   ['\\Gd{%c}', ['combining.diaresis', 'combining.grave.accent']], 
   ['\\Cd{%c}', ['combining.diaresis', 'combining.greek.perispomeni']], 
   ['\\Ar{%c}', ['combining.acute.accent', 'combining.reversed.comma.above']], 
   ['\\Gr{%c}', ['combining.grave.accent', 'combining.reversed.comma.above']], 
   ['\\Cr{%c}', ['combining.greek.perispomeni', 'combining.reversed.comma.above']], 
   ['\\As{%c}', ['combining.acute.accent', 'combining.comma.above']],
   ['\\Gs{%c}', ['combining.comma.above', 'combining.grave.accent']], 
   ['\\Cs{%c}', ['combining.comma.above', 'combining.greek.perispomeni']], 
   ['\\c{%c}', ['combining.inverted.breve.below']],
   ['\\ut{%cw}', ['combining.double.breve.below']],
   ['\\Ab{%c}', ['combining.acute.accent', 'combining.breve']],
   ['\\Gb{%c}', ['combining.breve', 'combining.grave.accent']],
   ['\\Arb{%c}', ['combining.acute.accent', 'combining.breve', 'combining.reversed.comma.above']],
   ['\\Grb{%c}', ['combining.breve', 'combining.grave.accent', 'combining.reversed.comma.above']],
   ['\\Asb{%c}', ['combining.acute.accent', 'combining.breve', 'combining.comma.above']],
   ['\\Gsb{%c}', ['combining.breve', 'combining.comma.above', 'combining.grave.accent']],
   ['\\Am{%c}', ['combining.acute.accent', 'combining.overline']],
   ['\\Gm{%c}', ['combining.grave.accent', 'combining.overline']],
   ['\\Cm{%c}', ['combining.greek.perispomeni', 'combining.overline']],
   ['\\Arm{%c}', ['combining.acute.accent', 'combining.overline', 'combining.reversed.comma.above']],
   ['\\Grm{%c}', ['combining.grave.accent', 'combining.overline', 'combining.reversed.comma.above']],
   ['\\Crm{%c}', ['combining.greek.perispomeni', 'combining.overline', 'combining.reversed.comma.above']],
   ['\\Asm{%c}', ['combining.acute.accent', 'combining.comma.above', 'combining.overline']],
   ['\\Gsm{%c}', ['combining.comma.above', 'combining.grave.accent', 'combining.overline']],
   ['\\Csm{%c}', ['combining.comma.above', 'combining.greek.perispomeni', 'combining.overline']],
   ['\\Sm{%c}', ['combining.comma.above', 'combining.overline']],
   ['\\Rm{%c}', ['combining.overline', 'combining.reversed.comma.above']],
   ['\\iS{%c}', ['combining.greek.ypogegrammeni']],
   ['\\d{%c}', ['combining.dot.below']],
   ['\\bd{%c}', ['combining.breve', 'combining.diaresis']],
   ['\\ring{%c}', ['combining.ring.below']]
]

accentmap.sort(key=lambda s: s[1])



def unicode_to_teubner(unicode_text):
   """Returns the given unicode string to a LaTeX document body using
the Teubner style for representing Greek characters and accents. Signature:

  ``unicode_to_teubner (unicode_text)``

The returned LaTeX code does not contain the LaTeX header. To create
a complete LaTeX document, you can use the following code:

.. code:: Python

   # LaTeX header
   print "\documentclass[10pt]{article}"
   print "\usepackage[polutonikogreek]{babel}"
   print "\usepackage[or]{teubner}"
   print "\\\\begin{document}"
   print "\selectlanguage{greek}"

   # document body
   print unicode_to_teubner(unicode_string)

   # LaTex footer
   print "\end{document}"

"""
   import unicodedata

   output = u""
   combinewith = []
   maincharacter = None
   i = 0
   while i < len(unicode_text):
      character = unicode_text[i]
      try:
         name_unicode = unicodedata.name(character)
      except:
         if character == "\n":
            output += " "

      name = name_unicode.lower()
      name = name.replace(" ", ".")
      
      
      if name.find("combining") == -1: #non-combining character
         if maincharacter != None and len(combinewith) > 0:
            #do lookup
            combinewith.sort()
            for format,combination in accentmap:
               if combination == combinewith:
                  try:
                     output += format % charactermap[maincharacter]
                  except KeyError:
                     sys.stderr.write("Teubner: Unknown character '%s'\n" % maincharacter)
                  break

            maincharacter = None
            combinewith = []

         elif maincharacter != None:
            try:
               output += charactermap[maincharacter]
               maincharacter = None
            except KeyError:
               sys.stderr.write("Teubner: Unknown character '%s'\n" % maincharacter)

         maincharacter = name_unicode
            
      else: #combining character
         if maincharacter != None:
            combinewith.append(name)
         else:
            output += "e"

      i += 1
   return output



if __name__ == "__main__":
   import unicodedata
   teststr = u"ἔθαψε, ὡς οἰκὸς ἦν"


   print unicode_to_teubner(unicodedata.normalize("NFD", teststr))

   for a in accentmap:
      sort = sorted(a[1])
#unicodedata.normalize(u"aäb", "NFD"))

#!/bin/bash

 saxonb-xslt  -xsl:/home/broberts/rigaudon/Scripts/exclude_glyphs.xsl  -ext:on  -s:$2 -o:$3 glyph_name=$1

#!/bin/bash
#Give the percentage complete of hocr conversion process by counting jp2 files and hocr files 

pages=`ls -1 /usr/local/OCR_Processing/Texts/AllGreekFromArchive/${1}_hocr | wc -l`
images=`ls -1 /usr/local/OCR_Processing/Texts/AllGreekFromArchive/${1}_jp2 | wc -l`
echo -n "$1: "
echo "scale = 2; $pages / $images " | bc

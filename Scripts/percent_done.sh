#!/bin/bash
#Give the percentage complete of hocr conversion process by counting jp2 files and hocr files 

pages=`find /usr/local/OCR_Processing/Texts/AllGreekFromArchiveCombined/*_hocr -name "*.html" | wc -l`
imagesJ2=`find   /usr/local/OCR_Processing/Texts/AllGreekFromArchiveCombined/*_jp2 -name "*.jp2" | wc -l`
imagesTif=`find   /usr/local/OCR_Processing/Texts/AllGreekFromArchiveCombined/*_tif -name "*.tif" | wc -l`
echo $pages $images
echo "scale = 2; 100 * $pages / ($imagesJ2 + $imagesTif) " | bc

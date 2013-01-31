#!/bin/bash
LATIN_HOCR_DIR=$1
GREEK_HOCR_DIR=$2
OUTPUT_DIR=$3
for file in `ls $LATIN_HOCR_DIR/`
 do echo "${file%.*}"
GREEK_FILE=$GREEK_HOCR_DIR/output-${file%.*}*

if [ -e $GREEK_FILE ] 
then
~/rigaudon/Scripts/munge_hocr.py   $LATIN_HOCR_DIR/${file%.*}.html $GREEK_HOCR_DIR/output-${file%.*}* /tmp/$file > /tmp/debug
xsltproc ~/rigaudon/Scripts/add_hocr_css.xsl /tmp/$file > $OUTPUT_DIR/${file%.*}.html
 rm /tmp/$file
fi
done

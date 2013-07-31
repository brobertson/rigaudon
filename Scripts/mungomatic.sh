#!/bin/bash
LATIN_HOCR_DIR=$1
GREEK_HOCR_DIR=$2
OUTPUT_DIR=$3

if [ $MIX_HOCR = "False" ]
then
	echo 'not doing HOCR mixing'
	cp $GREEK_HOCR_DIR/* $OUTPUT_DIR

else
	echo 'doing HOCR mixing'
	for file in `ls $LATIN_HOCR_DIR/`
 		do echo "$file"
		GREEK_FILE=$GREEK_HOCR_DIR/$file

		if [ -e $GREEK_FILE ] 
		then
			$RIGAUDON_HOME/Scripts/munge_hocr.py   $LATIN_HOCR_DIR/$file $GREEK_HOCR_DIR/$file /tmp/$file 
			xsltproc $RIGAUDON_HOME/Scripts/add_hocr_css.xsl /tmp/$file > $OUTPUT_DIR/$file
			rm /tmp/$file

		else 
			echo "$GREEK_FILE doesn't exist"
		fi
	done
fi

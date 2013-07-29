#!/bin/bash

echo "Exporting folder names for $CLASSIFIER_FILE"

#start prep
filename=$(basename $CLASSIFIER_FILE)
export filename=${filename%.*}
export barebookname=${BOOK_NAME%%_jp2}
export JPG_GRAY_IMAGES=$BOOK_DIR/${barebookname}_gray
export JPG_COLOR_IMAGES=$BOOK_DIR/${barebookname}_color
export HOCR_OUTPUT=$BOOK_DIR/${DATE}_${filename}_raw_hocr_output
export PRIMARY_OUTPUT=$BOOK_DIR/${DATE}_${filename}_txt_output
export SECONDARY_OUTPUT=$BOOK_DIR/${DATE}_${filename}_output_tc
export TESS_OUTPUT=$BOOK_DIR/tess_eng_output
export HOCR_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_hocr_output
export HOCR_BLENDED=$BOOK_DIR/${DATE}_${filename}_blended_hocr_output
export TEXT_BLENDED=$BOOK_DIR/${DATE}_${filename}_blended_text_output
export SPELLCHECKED_HOCR_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_hocr_output_spellchecked
export COMBINED_HOCR=$BOOK_DIR/${DATE}_${filename}_combined_hocr_output
export TEXT_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_text_output
export ABBYY_DATA=`dirname $BOOK_DIR`/${barebookname}_hocr
export RELATIVE_HOCR_SELECTED=${DATE}_${filename}_selected_hocr_output
export RELATIVE_SPELLCHECKED_HOCR_SELECTED=${DATE}_${filename}_selected_hocr_output_spellchecked
export RELATIVE_COMBINED_HOCR=${DATE}_${filename}_combined_hocr_output
export RELATIVE_TEXT_SELECTED=${DATE}_${filename}_selected_text_output
export RELATIVE_HOCR_OUTPUT=${DATE}_${filename}_raw_hocr_output
export RELATIVE_HOCR_BLENDED=${DATE}_${filename}_blended_hocr_output
export RELATIVE_TEXT_BLENDED=${DATE}_${filename}_blended_text_output
export RELATIVE_PRIMARY_OUTPUT=${DATE}_${filename}_txt_output
export RELATIVE_SECONDARY_OUTPUT=${DATE}_${filename}_output_tc
export RELATIVE_TESS_OUTPUT=tess_eng_output
export CSV_FILE=$SECONDARY_OUTPUT/${DATE}_${filename}_summary.csv
export GRAPH_IMAGE_FILE=$HOCR_SELECTED/${DATE}_${filename}_summary.png
export GRAPH_IMAGE_FILE_3D=$HOCR_SELECTED/3d.png
export DICTIONARY_FILE=/home/fbaumgardt/MORPHEUS_DUMP_PLUS-greek-dictionary-with-bogus-freq.txt
export SPELLCHECK_FILE=$TEXT_SELECTED/${DATE}_${filename}_spellcheck.csv
export SIDE_BY_SIDE_VIEW=$BOOK_DIR/${barebookname}_${DATE}_${filename}_sidebyside
export RELATIVE_SIDE_BY_SIDE_VIEW=${barebookname}_${DATE}_${filename}_sidebyside
#touch $BOOK_DIR/filelist.txt
rm -rf $PRIMARY_OUTPUT > /dev/null
rm -rf $SECONDARY_OUTPUT > /dev/null 
rm -rf $HOCR_OUTPUT > /dev/null
rm -rf $HOCR_BLENDED > /dev/null
rm -rf $TEXT_BLENDED > /dev/null
rm -rf $HOCR_SELECTED > /dev/null
rm -rf $SPELLCHECKED_HOCR_SELECTED > /dev/null
rm -rf $COMBINED_HOCR > /dev/null
rm -rf $TEXT_SELECTED > /dev/null
rm -rf $TESS_OUTPUT > /dev/null
#rm -rf $JPG_GRAY_IMAGES > /dev/null
#rm -rf $JPG_COLOR_IMAGES > /dev/null
rm  -rf $SIDE_BY_SIDE_VIEW > /dev/null


mkdir $HOCR_OUTPUT
mkdir  $PRIMARY_OUTPUT
mkdir  $SECONDARY_OUTPUT
mkdir $TESS_OUTPUT > /dev/null
mkdir $HOCR_SELECTED
mkdir $HOCR_BLENDED
mkdir $TEXT_BLENDED
mkdir $SPELLCHECKED_HOCR_SELECTED
mkdir $COMBINED_HOCR
mkdir $TEXT_SELECTED
mkdir $SIDE_BY_SIDE_VIEW
#mkdir $JPG_GRAY_IMAGES
#mkdir $JPG_COLOR_IMAGES

echo $barebookname
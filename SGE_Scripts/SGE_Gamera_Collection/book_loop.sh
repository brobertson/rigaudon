#!/usr/bin/bash
#start prep
filename=$(basename $CLASSIFIER_FILE)
export filename=${filename%.*}
export barebookname=${BOOK_NAME%%_jp2}
export JPG_GRAY_IMAGES=$BOOK_DIR/${barebookname}_gray
export JPG_COLOR_IMAGES=$BOOK_DIR/${barebookname}_color
export HOCR_OUTPUT=$BOOK_DIR/${DATE}_${filename}_hocr_output
export PRIMARY_OUTPUT=$BOOK_DIR/${DATE}_${filename}_txt_output
export SECONDARY_OUTPUT=$BOOK_DIR/${DATE}_${filename}_output_tc
export TESS_OUTPUT=$BOOK_DIR/tess_eng_output
export HOCR_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_hocr_output
export SPELLCHECKED_HOCR_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_hocr_output_spellchecked
export COMBINED_HOCR=$BOOK_DIR/${DATE}_${filename}_combined_hocr_output
export TEXT_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_text_output
export ABBYY_DATA=`dirname $BOOK_DIR`/${barebookname}_hocr
export RELATIVE_HOCR_SELECTED=${DATE}_${filename}_selected_hocr_output
export RELATIVE_SPELLCHECKED_HOCR_SELECTED=${DATE}_${filename}_selected_hocr_output_spellchecked
export RELATIVE_COMBINED_HOCR=${DATE}_${filename}_combined_hocr_output
export RELATIVE_TEXT_SELECTED=${DATE}_${filename}_selected_text_output
export RELATIVE_HOCR_OUTPUT=${DATE}_${filename}_hocr_output
export RELATIVE_PRIMARY_OUTPUT=${DATE}_${filename}_txt_output
export RELATIVE_SECONDARY_OUTPUT=${DATE}_${filename}_output_tc
export RELATIVE_TESS_OUTPUT=tess_eng_output
export CSV_FILE=$SECONDARY_OUTPUT/${DATE}_${filename}_summary.csv
export GRAPH_IMAGE_FILE=$HOCR_SELECTED/${DATE}_${filename}_summary.png
#export DICTIONARY_FILE=/usr/local/OCR_Processing/Dictionary/MORPHEUS_DUMP_PLUS-greek-dictionary-with-bogus-freq.txt
export SPELLCHECK_FILE=$TEXT_SELECTED/${DATE}_${filename}_spellcheck.csv
export SIDE_BY_SIDE_VIEW=$BOOK_DIR/${barebookname}_${DATE}_${filename}_sidebyside
export RELATIVE_SIDE_BY_SIDE_VIEW=${barebookname}_${DATE}_${filename}_sidebyside
#touch $BOOK_DIR/filelist.txt
rm -rf $PRIMARY_OUTPUT > /dev/null
rm -rf $SECONDARY_OUTPUT > /dev/null 
rm -rf $HOCR_OUTPUT > /dev/null
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
mkdir $SPELLCHECKED_HOCR_SELECTED
mkdir $COMBINED_HOCR
mkdir $TEXT_SELECTED
mkdir $SIDE_BY_SIDE_VIEW
#mkdir $JPG_GRAY_IMAGES
#mkdir $JPG_COLOR_IMAGES

#Job names
JOB_NAME_BASE=$barebookname-$DATE
OCR_BATCH_JOB_NAME=$JOB_NAME_BASE-ocr-batch
LYNX_DUMP_JOB_NAME=$JOB_NAME_BASE-lynx-dump
SUMMARY_SPLIT_JOB_NAME=$JOB_NAME_BASE-summary-split
SPELLCHECK_JOB_NAME=$JOB_NAME_BASE-spellcheck
SPELLREPLACE_JOB_NAME=$JOB_NAME_BASE-spellreplace
COMBINE_GREEK_AND_LATIN_JOB_NAME=$JOB_NAME_BASE-combine-hocrs
POSTPROCESS_JOB_NAME=$JOB_NAME_BASE-postprocess

qstat -r | grep `cat $CURRENT_JOB_FILE`
RETVAL=$?
if [ $RETVAL -eq 0 ]
then
        echo "There is a book `cat $CURRENT_JOB_FILE` in process"
	PREV_BOOK_HOLD="-hold_jid `cat $CURRENT_JOB_FILE`-postprocess"
else
        echo "There is not a book in process"
	PREV_BOOK_HOLD=""
fi


echo "Previous book hold: $PREV_BOOK_HOLD"

if [ ${MIX_HOCR:=False} = "True" ] 
then
	export DRIVER_HOCR_IS_LATINSCRIPT=`$RIGAUDON_HOME/Scripts/has_latin_script.py $barebookname`
	echo "Latin-script source hocr file?: $DRIVER_HOCR_IS_LATINSCRIPT"
	if [ $DRIVER_HOCR_IS_LATINSCRIPT = "False" ]
	then
		MIX_HOCR="False"
		echo "Not doing HOCR mixing ..."
	fi
else
	echo "Not doing HOCR mixing because MIX_HOCR is set to $MIX_HOCR"
fi

if [ ! -f $DICTIONARY_FILE ]
then
  echo "Dictionary file $DICTIONARY_FILE doesn't exist"
  exit 1
fi

#DEBUG
#cat $FILE_LIST
#echo $FILE_COUNT
#echo "CSV_FILE: $CSV_FILE"
#end prep
#This does an array job the size of the number of files in the book
#directory
qsub -N $OCR_BATCH_JOB_NAME  -p -200 $PREV_BOOK_HOLD -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -t 1-$FILE_COUNT -V $RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/qsubed_job.sh

#Now we use this script to:
#1. Convert the hocr output to plain text
#2. Evaluate the plain text with Federico's code
#3. Save comma-separated pairs of textfile name and score 
qsub -N $LYNX_DUMP_JOB_NAME -p -150 -hold_jid $OCR_BATCH_JOB_NAME -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash  -V  $RIGAUDON_HOME/Scripts/lynx_dump.sh $HOCR_OUTPUT $PRIMARY_OUTPUT $SECONDARY_OUTPUT $CSV_FILE

#This script takes the above-generated csv file and uses it to:
#1. Copy the highest-scoring text file to the 'selected' dir
#2. Copy the corresponding highest-scoring hocr file to the 'selected' dir
#3. Make a graph of page# vs. score for these highest-scoring pages.
qsub -N $SUMMARY_SPLIT_JOB_NAME -p -100 -hold_jid  $LYNX_DUMP_JOB_NAME  -b y -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -V /usr/bin/python $RIGAUDON_HOME/Scripts/summary_split.py $CSV_FILE $HOCR_OUTPUT $PRIMARY_OUTPUT $HOCR_SELECTED $TEXT_SELECTED $GRAPH_IMAGE_FILE

qsub -N $SPELLCHECK_JOB_NAME  -hold_jid  $SUMMARY_SPLIT_JOB_NAME -b y -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -V /usr/bin/python $RIGAUDON_HOME/Scripts/read_dict5.py $DICTIONARY_FILE $TEXT_SELECTED/output*  $SPELLCHECK_FILE

qsub -N $SPELLREPLACE_JOB_NAME -hold_jid  $SPELLCHECK_JOB_NAME -b y -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -V /usr/bin/python $RIGAUDON_HOME/Scripts/spellcheck_hocr.py $SPELLCHECK_FILE $HOCR_SELECTED   $SPELLCHECKED_HOCR_SELECTED

qsub -N $COMBINE_GREEK_AND_LATIN_JOB_NAME -hold_jid $SPELLREPLACE_JOB_NAME -b y -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -V  $RIGAUDON_HOME/Scripts/mungomatic.sh $ABBYY_DATA $SPELLCHECKED_HOCR_SELECTED $COMBINED_HOCR

qsub -N $POSTPROCESS_JOB_NAME -p 0 -hold_jid  $COMBINE_GREEK_AND_LATIN_JOB_NAME  -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -V $RIGAUDON_HOME/Scripts/post_qsub_processing.sh
echo $JOB_NAME_BASE > $CURRENT_JOB_FILE 

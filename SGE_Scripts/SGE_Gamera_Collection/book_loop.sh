#!/usr/bin/bash
#start prep
filename=$(basename $CLASSIFIER_FILE)
filename=${filename%.*}
barebookname=${BOOK_NAME%%_jp2}
export HOCR_OUTPUT=$BOOK_DIR/${DATE}_${filename}_hocr_output
export PRIMARY_OUTPUT=$BOOK_DIR/${DATE}_${filename}_txt_output
export SECONDARY_OUTPUT=$BOOK_DIR/${DATE}_${filename}_output_tc
export TESS_OUTPUT=$BOOK_DIR/tess_eng_output
export HOCR_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_hocr_output
export TEXT_SELECTED=$BOOK_DIR/${DATE}_${filename}_selected_text_output
export ABBYY_DATA=`dirname $BOOK_DIR`/${barebookname}_hocr
export RELATIVE_HOCR_SELECTED=${DATE}_${filename}_selected_hocr_output
export RELATIVE_TEXT_SELECTED=${DATE}_${filename}_selected_text_output
export RELATIVE_HOCR_OUTPUT=${DATE}_${filename}_hocr_output
export RELATIVE_PRIMARY_OUTPUT=${DATE}_${filename}_txt_output
export RELATIVE_SECONDARY_OUTPUT=${DATE}_${filename}_output_tc
export RELATIVE_TESS_OUTPUT=tess_eng_output
export CSV_FILE=$SECONDARY_OUTPUT/${DATE}_${filename}_summary.csv
export GRAPH_IMAGE_FILE=$HOCR_SELECTED/${DATE}_${filename}_summary.png
#touch $BOOK_DIR/filelist.txt
rm -rf $PRIMARY_OUTPUT > /dev/null
rm -rf $SECONDARY_OUTPUT > /dev/null 
rm -rf $HOCR_OUTPUT > /dev/null
rm -rf $HOCR_SELECTED > /dev/null
rm -rf $TEXT_SELECTED > /dev/null
rm -rf $TESS_OUTPUT > /dev/null
mkdir $HOCR_OUTPUT
mkdir  $PRIMARY_OUTPUT
mkdir  $SECONDARY_OUTPUT
mkdir $TESS_OUTPUT > /dev/null
mkdir $HOCR_SELECTED
mkdir $TEXT_SELECTED
#DEBUG
#cat $FILE_LIST
#echo $FILE_COUNT
#echo "CSV_FILE: $CSV_FILE"
#end prep
#This does an array job the size of the number of files in the book
#directory
qsub -sync y -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -t 1-$FILE_COUNT -V $RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/qsubed_job.sh

#Now we use this script to:
#1. Convert the hocr output to plain text
#2. Evaluate the plain text with Federico's code
#3. Save comma-separated pairs of textfile name and score 
$RIGAUDON_HOME/Scripts/lynx_dump.sh $HOCR_OUTPUT $PRIMARY_OUTPUT $SECONDARY_OUTPUT $CSV_FILE

#This script takes the above-generated csv file and uses it to:
#1. Copy the highest-scoring text file to the 'selected' dir
#2. Copy the corresponding highest-scoring hocr file to the 'selected' dir
#3. Make a graph of page# vs. score for these highest-scoring pages.
$RIGAUDON_HOME/Scripts/summary_split.py $CSV_FILE $HOCR_OUTPUT $SECONDARY_OUTPUT $HOCR_SELECTED $TEXT_SELECTED $GRAPH_IMAGE_FILE

cp $CSV_FILE $TEXT_SELECTED
#Now report using email.

echo "$BOOK_DIR $DATE done using $filename classifier. `ls $HOCR_SELECTED | wc -l` files created with total score `cat $HOCR_SELECTED/best_scores_sum.txt`." | mutt -s "$BOOK_DIR at sharcnet" -a $GRAPH_IMAGE_FILE -- bruce.g.robertson@gmail.com
#echo "$BOOK_DIR $DATE done" | mail bruce.g.robertson@gmail.com -s "$BOOK_DIR processing"
cd $BOOK_DIR
tar -zcf $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_hocr_and_txt.tar.gz  $RELATIVE_HOCR_SELECTED $RELATIVE_TEXT_SELECTED 
tar -zcf  $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_full.tar.gz $RELATIVE_HOCR_OUTPUT $RELATIVE_PRIMARY_OUTPUT $RELATIVE_SECONDARY_OUTPUT $RELATIVE_HOCR_SELECTED $RELATIVE_TEXT_SELECTED
cd -
THIS_COMMAND="mkdir /home/brucerob/Rigaudon/${BOOK_NAME}"
ssh heml $THIS_COMMAND
cd $BOOK_DIR
scp -r ${DATE}_${filename}_selected_hocr_output heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r  ${DATE}_${filename}_selected_text_output heml:/home/brucerob/Rigaudon/${BOOK_NAME}
rm -rf  $HOCR_OUTPUT
rm -rf  $PRIMARY_OUTPUT
rm -rf  $SECONDARY_OUTPUT
rm -rf  $TESS_OUTPUT > /dev/null
rm -rf  $HOCR_SELECTED
rm -rf  $TEXT_SELECTED

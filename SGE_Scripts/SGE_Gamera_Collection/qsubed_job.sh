#!/bin/bash
#$ -cwd
#$ -j y
#$ -l h_rt=00:08:00
echo "CLASSIFIER_FILE: $CLASSIFIER_FILE"
classifier_filename=$(basename $CLASSIFIER_FILE)
classifier_filename=${classifier_filename%.*}
HOCR_OUTPUT=$BOOK_DIR/${classifier_filename}_hocr_output
PRIMARY_OUTPUT=$BOOK_DIR/${classifier_filename}_txt_output
SECONDARY_OUTPUT=$BOOK_DIR/${classifier_filename}_output_tc
TESS_OUTPUT=$BOOK_DIR/tess_eng_output
BOOK_DIR_TRUNC=$(basename $BOOK_DIR)
#NUM=`printf "%08d" $SGE_TASK_ID`
#NUM=`printf "%08d" 123`
IMAGE_FILENAME=`head -$SGE_TASK_ID $FILE_LIST | tail -1`
TRUNC_IMAGE_FILENAME=$(basename $IMAGE_FILENAME)
TRUNC_IMAGE_FILENAME=${TRUNC_IMAGE_FILENAME%.*}
#HOCR_FILENAME=/home/broberts/scratch/Tesseract_3_01_output_2012_03_30/${BOOK_DIR_TRUNC}/${BOOK_DIR_TRUNC}_${TRUNC_IMAGE_FILENAME}_tess.html
if [ -e  $IMAGE_FILENAME ] 
then
TESSFILE=${TESS_OUTPUT}/out_tess_$TRUNC_IMAGE_FILENAME
#The tesseract file will not change with different Gamera classifiers
#So we check to make sure it doesn't already exist
if [ ! -e $TESSFILE ] 
then
   tesseract  $IMAGE_FILENAME   $TESSFILE -l eng hocr 
fi

python  /usr/local/bin/greekocr4gamera.py -x $CLASSIFIER_FILE/classifier_glyphs.xml  --settings $CLASSIFIER_FILE/optimized_settings.xml  --split --autogroup -s --hocrout -u $HOCR_OUTPUT/output- $IMAGE_FILENAME #> /dev/null
lynx --dump $HOCR_OUTPUT/output-$TRUNC_IMAGE_FILENAME.html > $PRIMARY_OUTPUT/output-$TRUNC_IMAGE_FILENAME.txt
/usr/bin/java  -jar /home/broberts/Federicos-evaluator/tg.jar <   $PRIMARY_OUTPUT/output-$TRUNC_IMAGE_FILENAME.txt  >  $SECONDARY_OUTPUT/output-$TRUNC_IMAGE_FILENAME.txt  
fi

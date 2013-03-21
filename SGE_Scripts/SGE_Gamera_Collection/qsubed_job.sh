#!/bin/bash
#$ -cwd
#$ -j y
#$ -l h_rt=01:18:00
#$ -l h_vmem=1G
echo "CLASSIFIER_FILE: $CLASSIFIER_FILE"
echo "GAMERA CMDS: $GAMERA_CMDS"
echo "HOCR: $HOCR"
classifier_filename=$(basename $CLASSIFIER_FILE)
classifier_filename=${classifier_filename%.*}
#HOCR_OUTPUT=$BOOK_DIR/${classifier_filename}_hocr_output
#PRIMARY_OUTPUT=$BOOK_DIR/${classifier_filename}_txt_output
#SECONDARY_OUTPUT=$BOOK_DIR/${classifier_filename}_output_tc
#TESS_OUTPUT=$BOOK_DIR/tess_eng_output
BOOK_DIR_TRUNC=$(basename $BOOK_DIR)
#NUM=`printf "%08d" $SGE_TASK_ID`
#NUM=`printf "%08d" 123`
IMAGE_FILENAME=`head -$SGE_TASK_ID $FILE_LIST | tail -1`
TRUNC_IMAGE_FILENAME=$(basename $IMAGE_FILENAME)
TRUNC_IMAGE_FILENAME=${TRUNC_IMAGE_FILENAME%.*}
#HOCR_FILENAME=/home/broberts/scratch/Tesseract_3_01_output_2012_03_30/${BOOK_DIR_TRUNC}/${BOOK_DIR_TRUNC}_${TRUNC_IMAGE_FILENAME}_tess.html
OUTPUT_STUB=""
if [ -e  $IMAGE_FILENAME ] 
then
TESSFILE=${TESS_OUTPUT}/out_tess_$TRUNC_IMAGE_FILENAME
echo "The image base fileame is `basename $IMAGE_FILENAME`"
if ! [[ `basename "$IMAGE_FILENAME"` == *_* ]]
then  
OUTPUT_STUB="_"
fi
#The tesseract file will not change with different Gamera classifiers
#So we check to make sure it doesn't already exist
#
#The trick here is that if we give the output name /foo/bar/baz
#it saves under /foo/bar/baz.html

#if [ ! -e ${TESSFILE}.html ] 
#then
#   tesseract  $IMAGE_FILENAME   $TESSFILE -l eng hocr 
#fi

HOCR_COMMAND=""
if [ "$HOCR" = "ABBYY" ]; then
    HOCR_COMMAND=" --hocr ${ABBYY_DATA}/%s.html "
    echo "executing HOCR with command \'$HOCR_COMMAND\'"
fi

python  /usr/local/bin/greekocr4gamera.py -x $CLASSIFIER_FILE/classifier_glyphs.xml  --settings $CLASSIFIER_FILE/optimized_settings.xml -s ${GAMERA_CMDS}${HOCR_COMMAND} --hocrout -u $HOCR_OUTPUT/output-${OUTPUT_STUB} $IMAGE_FILENAME 
fi

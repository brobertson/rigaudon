#!/bin/bash
#$ -cwd
#$ -j y
#$ -l h_rt=01:00:00
#$ -l h_vmem=1G
# here, we take the SGE_TSK_ID-th line in the file list to be our filename.
# Neat, huh?
BASE_HOCR_FILENAME=`ls -1 $HOCR_SELECTED/*html | head -$SGE_TASK_ID | tail -1`
echo BASE_HOCR_FILENAME: $BASE_HOCR_FILENAME
TRUNC_BASE_HOCR_FILENAME=$(basename $BASE_HOCR_FILENAME)
echo TRUNC BASE HOCR FILENAME: $TRUNC_BASE_HOCR_FILENAME
TRUNC_BASE_HOCR_FILENAME_NO_EXT=${TRUNC_BASE_HOCR_FILENAME%.*}
BLENDED_OUTPUT_FILE=$HOCR_BLENDED/$TRUNC_BASE_HOCR_FILENAME
echo BLENDED_OUTPUT_FILE: $BLENDED_OUTPUT_FILE
# this takes a filename like
# output-septemadthebased00aescuoft_0057_jp2_thresh_99.html
# and generates 
# output-septemadthebased00aescuoft_0042*
# so we can select the similar files of different thresholds
	 OTHER_HOCRS_GLOB=`echo $TRUNC_BASE_HOCR_FILENAME | python -c "import sys;[sys.stdout.write('_'.join(line.split('_')[:2])+'*') for line in sys.stdin]"`
OTHER_HOCRS=$HOCR_OUTPUT/$OTHER_HOCRS_GLOB
echo OTHER_HOCRS: $OTHER_HOCRS
# we need: dictionary, base file, glommed other files, output file
python $RIGAUDON_HOME/Scripts/select_from_thresholds.py $DICTIONARY_FILE $BASE_HOCR_FILENAME $OTHER_HOCRS $BLENDED_OUTPUT_FILE
lynx --dump $BLENDED_OUTPUT_FILE > $TEXT_BLENDED/$TRUNC_BASE_HOCR_FILENAME_NO_EXT.txt


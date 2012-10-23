#!/usr/bin/bash
#start prep
filename=$(basename $CLASSIFIER_FILE)
filename=${filename%.*}
export HOCR_OUTPUT=$BOOK_DIR/${filename}_hocr_output
export PRIMARY_OUTPUT=$BOOK_DIR/${filename}_txt_output
export SECONDARY_OUTPUT=$BOOK_DIR/${filename}_output_tc
export TESS_OUTPUT=$BOOK_DIR/tess_eng_output
#touch $BOOK_DIR/filelist.txt
rm -rf $PRIMARY_OUTPUT > /dev/null
rm -rf $SECONDARY_OUTPUT > /dev/null 
rm -rf $HOCR_OUTPUT > /dev/null
mkdir $HOCR_OUTPUT
mkdir  $PRIMARY_OUTPUT
mkdir  $SECONDARY_OUTPUT
mkdir $TESS_OUTPUT

#DEBUG
#cat $FILE_LIST
#echo $FILE_COUNT

#end prep
qsub -o $OUTPUT_DIR -e $ERROR_DIR -S /bin/bash -t 1-$FILE_COUNT -V qsubed_job.sh
#qsub -S /bin/bash -t 1-$FILE_COUNT -v CLASSIFIER_FILE=$CLASSIFIER_FILE/,BOOK_DIR=$BOOK_DIR/,FILE_LIST=$FILE_LIST  qsubed_job.sh 
#qsub -S /bin/bash -t 1-2  -v CLASSIFIER_FILE=/home/broberts/philos_opera_0150_cnn_mnn_0200_cnn_mnn_250_cnn_mnn/,BOOK_DIR=/usr/local/OCR_Processing/Texts/Imagine/operaquaesupersu06phil_png_76/,FILE_LIST=/usr/local/OCR_Processing/Texts/Imagine/operaquaesupersu06phil_png_76/filelist.txt   qsubed_job.sh
#./federize.sh


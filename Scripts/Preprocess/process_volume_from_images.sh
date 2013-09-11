#!/bin/bash
#export HOCR="ABBYY" 
#export MIX_HOCR="True"

export HOCR="False"
export MIX_HOCR="False"
export DRIVER_HOCR_IS_LATINSCRIPT="True"
#export RIGAUDON_HOME=/home/broberts/rigaudon/
#export FBEVALUATOR_HOME=/home/broberts/Federicos-evaluator/
GAMERA_CMDS_DEFAULT=" --split --autogroup  --filter"
# --otsu  0.66,0.68,0.70,0.72,0.74,0.76,0.78,0.8,0.82,0.84,0.86,0.88,0.90,0.92,0.94,0.96,0.98,1.0,1.02,104,1.06,1.08,1.10,1.12,1.14,1.16,1.18" 
GAMERA_CMDS=$GAMERA_CMDS_DEFAULT
SCANTAILOR_CMDS_DEFAULT=" --threshold=20 --color-mode=black_and_white"
#color_grayscale  --white-margins --normalize-illumination"
export RAW_IMAGE_DIR=$1
export ID=$2
export META_FILE=$3
export CLASSIFIER_DIR=$4
export TEXT_STAGING_DIR=/usr/local/OCR_Processing/Texts/
export PROCESSING_DIR=$TEXT_STAGING_DIR/$ID
export STAGING_IMAGE_DIR=$PROCESSING_DIR/${ID}_stage
export PREPPED_IMAGE_DIR=$PROCESSING_DIR/${ID}_tif
export HOCR_DIR=$PROCESSING_DIR/${ID}_hocr
export TESS_BIN_DIR=/usr/local/bin

usage(){
	echo "Usage: $0 RAW_IMAGE_DIR ID_STRING METADATA_FILE.XML CLASSIFIER_DIR"
	exit 1
}

#Check for proper arguments
if [ $# -ne 4 ]; then
 echo "Improper number of arguments"
 usage
fi

if [ ! -d "$1" ]; then
  echo "Raw image directory not found"
  usage
fi

if [ ! -d "$4" ]; then
  echo "Classifier directory not found"
  usage
fi

if [ ! -d "$3" ]; then
  echo "Metadata file not found"
  usage
fi

#Download and preprocess the text images and data if they aren't downloaded yet
if [ ! -d $PROCESSING_DIR ]; then
  mkdir $PROCESSING_DIR
  cd $PROCESSING_DIR
  mkdir $STAGING_IMAGE_DIR
  echo "mogrifying raw files.."
  cd $RAW_IMAGE_DIR
  parallel convert {}  -morphology Open Diamond ${STAGING_IMAGE_DIR}/{} ::: *
 #  cp * ${STAGING_IMAGE_DIR}
  mkdir $PREPPED_IMAGE_DIR
  echo "Scantailoring the raw images..."
  parallel "scantailor-cli -v $SCANTAILOR_CMDS_DEFAULT {} $PREPPED_IMAGE_DIR" ::: $STAGING_IMAGE_DIR/*
  rm -rf $PREPPED_IMAGE_DIR/cache
  echo "Done scantailor ... Now doing tesseract bbox generation" 
  rm -rf $STAGING_IMAGE_DIR  
cd $PREPPED_IMAGE_DIR
  #renaming and renumbering the scantailor output
  a=0
  for i in $PREPPED_IMAGE_DIR/*; do
    new=$(printf ${PREPPED_IMAGE_DIR}/${ID}_"%04d.tif" ${a}) #04 pad to length of 4
    mv ${i} ${new}
    let a=a+1
  done

#echo "mogrifiying..."
#mogrify  -morphology Open Diamond ${PREPPED_IMAGE_DIR}/*tif

  cp $META_FILE ${PREPPED_IMAGE_DIR}/${ID}_meta.xml

  mkdir $PROCESSING_DIR/${ID}_tess  
  #ln -s $PROCESSING_DIR/${ID}_tess $HOCR_DIR
  #parallel $TESS_BIN_DIR/tesseract {} $PROCESSING_DIR/${ID}_tess/{.} -l eng+grc hocr ::: *tif 
  mkdir $PROCESSING_DIR/${ID}_tess_cleaned
  cd $PROCESSING_DIR/${ID}_tess
 # parallel python ~/rigaudon/Scripts/correct_tesseract_hocr_layout_errors.py {} ../${ID}_tess_cleaned/{} ::: *
  cd -
  #ln -s $PROCESSING_DIR/${ID}_tess_cleaned $HOCR_DIR
fi

echo 'Submitting job to Grid Engine'
$RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/process_collection.sh $PROCESSING_DIR $CLASSIFIER_DIR

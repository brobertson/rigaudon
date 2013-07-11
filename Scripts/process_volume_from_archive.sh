#!/bin/bash

export HOCR="ABBYY" 
export RIGAUDON_HOME=/home/broberts/rigaudon/
export FBEVALUATOR_HOME=/home/broberts/Federicos-evaluator/
GAMERA_CMDS_DEFAULT=" --split --autogroup  --filter --otsu  0.69,0.72,0.75,0.78,0.81,0.84,0.87,0.91,0.94,0.97,1.0,1.03,1.05,1.07,1.09,1.12,1.15,1.17,1.19,1.22"
${GAMERA_CMDS:=$GAMERA_CMDS_DEFAULT}
export ARCHIVE_ID=$1
export CLASSIFIER_DIR=$2
export TEXT_STAGING_DIR=/usr/local/OCR_Processing/Texts/

export PROCESSING_DIR=$TEXT_STAGING_DIR/$ARCHIVE_ID

if [ -e $TEXT_STAGING_DIR/AllGreekFromArchiveCombined/${ARCHIVE_ID}_hocr ]; then
  mkdir $PROCESSING_DIR
  cd $PROCESSING_DIR
  ln -s $TEXT_STAGING_DIR/AllGreekFromArchiveCombined/${ARCHIVE_ID}* .
  cd -
fi

#Download and preprocess the text images and data if they aren't downloaded yet
if [ ! -d $PROCESSING_DIR ]; then
  mkdir $PROCESSING_DIR
  cd $PROCESSING_DIR
  echo "Attempting to download $ARCHIVE_ID from archive.org"
  wget --spider "http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_jp2.zip" 2>  /tmp/response.txt 
  grep '200 OK' /tmp/response.txt | wc -l
  badDL=$?
  echo "status: $badDL"
  if [ "$badDL" == "0" ]; then
    #the jp2 archive is not available, so we'll guess that it's tiff
    wget http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_tif.zip
  else
    wget  http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_jp2.zip
  fi
  wget http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_meta.xml
  sleep 20
  wget http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_abbyy.gz
  echo 'Uncompressing ...'
  gunzip *gz
  unzip *zip
  
  echo "Converting abbyy file to hocr"
  HOCR_DIR=${ARCHIVE_ID}_hocr
  #echo "hocrDir: $hocrDir"
  mkdir $HOCR_DIR
  python $RIGAUDON_HOME/Scripts/abbyy2hocr_etree.py ${ARCHIVE_ID}_abbyy $HOCR_DIR  ${ARCHIVE_ID}_jp2
fi
#done downloading and pre-processing

echo 'Submitting job to Grid Engine'
$RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/process_collection.sh $PROCESSING_DIR $CLASSIFIER_DIR

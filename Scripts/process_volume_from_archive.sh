#!/bin/bash
export HOCR="ABBYY" 
export RIGAUDON_HOME=/home/broberts/rigaudon/
export GAMERA_CMDS=" --split --autogroup  --filter --otsu  0.78,0.80,0.83,0.85,0.87,0.90,0.92,0.95,0.97,1.0,1.03,1.05,1.07,1.09,1.12"
#0.65,0.67,0.70,0.72,0.75,0.78,0.80,0.83,0.85,0.87,0.90,0.92,0.95,0.97,1.0,1.03,1.05,1.07,1.09,1.12,1.15,1.17"
#0.91,0.95,1.0,1.05,1.08" 
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
  curl -IL "http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_jp2.zip" >  /tmp/response.txt 
  grep HTTP/1.1 /tmp/response.txt | tail -1 | grep 404
  badDL=$?
  echo "status: $badDL"
  if [ "$badDL" -eq "0" ]; then
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

  echo "Flattening abbyy file"
  $RIGAUDON_HOME/Scripts/flatten_for_abbyy.sh ${ARCHIVE_ID}_abbyy 
  echo 'Converting abbyy.xml file to hocr'
  $RIGAUDON_HOME/Scripts/abbyy_to_hocr.sh ${ARCHIVE_ID}_abbyy_flat.xml
  echo 'Renumbering HOCR files to concur with image files'
  $RIGAUDON_HOME/Scripts/renumber_hocr_out.sh ${ARCHIVE_ID}_jp2
fi
#done downloading and pre-processing

echo 'Submitting job to Grid Engine'
$RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/process_collection.sh $PROCESSING_DIR $CLASSIFIER_DIR

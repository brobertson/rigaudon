#!/bin/bash

if [ -e $TEXT_STAGING_DIR/AllGreekFromArchiveCombined/${ARCHIVE_ID}_hocr ]; then
  mkdir $PROCESSING_DIR
  cd $PROCESSING_DIR
  ln -s $TEXT_STAGING_DIR/AllGreekFromArchiveCombined/${ARCHIVE_ID}* .
  cd -
fi
echo "PROCESSING_DIR: ${PROCESSING_DIR}"
#Download and preprocess the text images and data if they aren't downloaded yet
if [ ! -d $PROCESSING_DIR ]; then
  mkdir $PROCESSING_DIR
  cd $PROCESSING_DIR
  echo "Attempting to download $ARCHIVE_ID from archive.org"
  wget -nv --spider "http://www.archive.org/download/${ARCHIVE_ID}/${ARCHIVE_ID}_jp2.zip" 2>  ${OUTPUT_DIR}/response.txt 
  badDL=`grep '200 OK' ${OUTPUT_DIR}/response.txt | wc -l`
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
  #echo "Flattening abbyy file"
  #$RIGAUDON_HOME/Scripts/flatten_for_abbyy.sh ${ARCHIVE_ID}_abbyy 
  #echo 'Converting abbyy.xml file to hocr'
  #$RIGAUDON_HOME/Scripts/abbyy_to_hocr.sh ${ARCHIVE_ID}_abbyy_flat.xml
  #echo 'Renumbering HOCR files to concur with image files'
  #$RIGAUDON_HOME/Scripts/renumber_hocr_out.sh ${ARCHIVE_ID}_jp2
fi
#done downloading and pre-processing

echo $PROCESSING_DIR
echo $CLASSIFIER_DIR

echo 'Submitting job to Grid Engine'
$RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/process_collection.sh $PROCESSING_DIR $CLASSIFIER_DIR

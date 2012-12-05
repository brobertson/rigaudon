#!/bin/bash
#This script takes as an argument an abbyy ocr output xml file in archive.org format (which doesn't have the 
#extension '.xml'). It makes a directory with the archivename + _hocr, then puts in it separate files for 
#each page of the input.
jp2InputFile=$1
#echo "jp2 file: $jp2InputFile"
archivePath=${jp2InputFile%%_jp2}
archive=$(basename $archivePath)
#echo "archive name: $archivePath"
hocrDir=${archivePath}_hocr
#echo "hocrDir: $hocrDir"
fileNum="_0100"
hocrFile=$hocrDir/${archive}_0100.html
jp2File=$jp2InputFile/${archive}_0100.jp2
if [ ! -f $jp2File ]
then 
  fileNum="_0050"
  hocrFile=$hocrDir/${archive}_0050.html
  jp2File=$jp2InputFile/${archive}_0050.jp2
fi 
#echo "archive: $archive"
storageDir=/usr/local/OCR_Processing/ArchSegImages
pngFile=${storageDir}/${archive}.png
convert $jp2File  $pngFile
python /home/broberts/rigaudon/Scripts/hocr_draw_boxes_complex.py $pngFile $hocrFile ${storageDir}/${archive}${fileNum}.png
rm $pngFile
#echo "made dir"
#cd $hocrDir
#echo "moved"
#saxonb-xslt -xsl:/home/broberts/rigaudon/Scripts/abbyy2hocr.xsl  -ext:on  $abbyyInputFile
#saxonb-xslt -xsl:/media/sf_Pictures/abbyy2hocr.xsl  -ext:on  /media/sf_Pictures/philodemiperipar00philuoft_abbyy

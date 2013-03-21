#!/bin/bash
if [[ -z $RIGAUDON_HOME ]]; then
  echo '$RIGAUDON_HOME not set. Exiting.'
  exit
fi

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
python $RIGAUDON_HOME/Scripts/hocr_draw_boxes_complex.py $pngFile $hocrFile ${storageDir}/${archive}${fileNum}.png
rm $pngFile

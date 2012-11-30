#This script takes as an argument an abbyy ocr output xml file in archive.org format (which doesn't have the 
#extension '.xml'). It makes a directory with the archivename + _hocr, then puts in it separate files for 
#each page of the input.
abbyyInputFile=$1
echo "input file: $abbyyInputFile"
archiveName=${abbyyInputFile%%_abbyy}
echo "archive name: $archiveName"
hocrDir=${archiveName}_hocr
echo "hocrDir: $hocrDir"
mkdir $hocrDir
echo "made dir"
cd $hocrDir
echo "moved"
saxonb-xslt -xsl:/home/broberts/rigaudon/Scripts/abbyy2hocr.xsl  -ext:on  $abbyyInputFile
#saxonb-xslt -xsl:/media/sf_Pictures/abbyy2hocr.xsl  -ext:on  /media/sf_Pictures/philodemiperipar00philuoft_abbyy

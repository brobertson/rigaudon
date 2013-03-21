#!/bin/bash
#This script takes as an argument an abbyy ocr output xml file in archive.org format (which doesn't have the 
#extension '.xml'). It makes a directory with the archivename + _hocr, then puts in it separate files for 
#each page of the input.
#Please note the need to do a xslt 1.0 transformation before the paging one. This is because the charParams elements are children of different nodes, and I found using the 'following' axis was brutally expensive.

#For big files, typical of this sort of data, you may need to do these two steps separately in order to avoid running out of memory.

if [[ -z $RIGAUDON_HOME ]]; then
  echo '$RIGAUDON_HOME not set. Exiting.'
  exit
fi
# Get time as a UNIX timestamp (seconds elapsed since Jan 1, 1970 0:00 UTC)
T="$(date +%s)"

abbyyInputFile=$1
echo "Starting input file: $abbyyInputFile"
archiveName=${abbyyInputFile%%_abbyy_flat.xml}
#echo "archive name: $archiveName"
hocrDir=${archiveName}_hocr
#echo "hocrDir: $hocrDir"
mkdir $hocrDir
#echo "made dir"
cd $hocrDir
saxonb-xslt -xsl:$RIGAUDON_HOME/Scripts/abbyy2hocr.xsl  -ext:on ../$abbyyInputFile  
echo -n "completed $hocrDir with `ls | wc -l` files"

#get time difference
T="$(($(date +%s)-T))"
#echo "Time in seconds: ${T}"

printf " in : %02d:%02d:%02d:%02d\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))"
cd -

#!/bin/bash
#usage renumber_hocr_out.sh directory_jp2/

# This script takes a _jp2 directory with files beginning with archiveID_0001.jp2
# or archiveID_0000.jp2 and assumes a corresponding *_hocr/ directory
# containing files with the names output-1.html, output-2.html, etc.
# It renames the latter files to correspond to the numbering and naming of the former,
# so for a directory beginning archiveID_0000.jp2, output-1.html would be renamed to
# archiveID_0000.html, etc.

# This is necessary in part because output numbering for xslt2 is yucky and because 
# the _jp2 directory might start with 0000.jp2 or with 0001.jp2!

array1=(`ls $1`)
hocrDir=${1%_jp2}_hocr
echo $hocrDir
array2=(`ls  $hocrDir | sed 's/output-//g'| sort -n`)

count=${#array1[@]}
for i in `seq 1 $count`
do
    nameWithoutExt=${array1[$i-1]%.jp2}
#    echo ${array1[$i-1]} ${array2[$i-1]} $nameWithoutExt.html
    mv -v $hocrDir/output-${array2[$i-1]} $hocrDir/$nameWithoutExt.html
done

#!/bin/bash
#To do
#This can't take a path on the input image. Ugh. 
#this can't deal with input our output images that have spaces in their filenames


#play with these yourself
LEPT_DIR=~/Downloads/leptonica-1.68
TMP_DIR=/tmp

#don't change these
filenamebase=$(basename $1)
filename=${1%.*}
filenamebase_noext=${filenamebase%.*}
#path=${1%/*}
#${1%.*}
lept_out=$TMP_DIR/lept_${filename}
pgm=$TMP_DIR/${filenamebase_noext}.pgm
unpapered_pgm=$TMP_DIR/unpapered_${filenamebase_noext}.pgm
unpapered_pbm=$TMP_DIR/unpapered_${filenamebase_noext}.pbm
#echo "file in: $1"
#echo "file out: $2"
#echo "lept_out: $lept_out"
#echo "pgm: $pgm"
#echo "unpapered_pgm: $unpapered_pgm"
#echo "unpapered_pbm: $unpapered_pbm"

$LEPT_DIR/prog/skewtest $1 $lept_out
convert $lept_out $pgm
unpaper --no-deskew --overwrite $pgm $unpapered_pgm
convert $unpapered_pgm $unpapered_pbm
convert $unpapered_pbm $2



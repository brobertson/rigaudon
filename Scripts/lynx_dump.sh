#!/bin/bash

#1. Convert the hocr output to plain text
#2. Evaluate the plain text with Federico's code
#3. Save comma-separated pairs of textfile name and score 

#usage: lynx_dump.sh $HOCR_OUTPUT $PLAINTEXT_OUTPUT $REGULARIZED_PLAINTEXT_OUTPUT $CSV_FILE

export JAVA_PATH=/usr/bin
for file in `ls $1`
do
TRUNC_FILENAME=$(basename $file)
TRUNC_FILENAME=${TRUNC_FILENAME%.*}

echo $TRUNC_FILENAME
lynx --dump $1/$file > $2/$TRUNC_FILENAME.txt
done

for file in `ls $2`
do
TRUNC_FILENAME=$(basename $file)
TRUNC_FILENAME=${TRUNC_FILENAME%.*}
#echo $2/$file into $3/$TRUNC_FILENAME.txt
/usr/bin/java  -jar /home/broberts/Federicos-evaluator/tg.jar <   $2/$file  >  $3/$TRUNC_FILENAME.txt
done

cd ~/Federicos-evaluator
echo "Federizing $3"
$JAVA_PATH/java -jar textevaluator.jar $3/ > /dev/null
cd -
for file in `ls $3/*eval.txt` 
do 
echo -n $file >> $4
echo -n "," >> $4
tail -n 1 $file | cut -c 9- >> $4
done

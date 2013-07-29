#!/bin/bash
#$ -cwd
#$ -j y
#$ -l h_rt=01:00:00
#$ -l h_vmem=18G
#1. Convert the hocr output to plain text
#2. Evaluate the plain text with Federico's code
#3. Save comma-separated pairs of textfile name and score 

#usage: lynx_dump.sh $HOCR_OUTPUT $PLAINTEXT_OUTPUT $REGULARIZED_PLAINTEXT_OUTPUT $CSV_FILE
if [[ -z $FBEVALUATOR_HOME ]]; then
  echo '$FBEVALUATOR_HOME not set. Exiting.'
  exit
fi

export JAVA_PATH=/usr/bin
for file in `ls $1`
do
TRUNC_FILENAME=$(basename $file)
TRUNC_FILENAME=${TRUNC_FILENAME%.*}

echo $TRUNC_FILENAME
lynx --dump $1/$file > $2/$TRUNC_FILENAME.txt
done

echo "regularizing files in $2 and putting into $3"
for file in `ls $2`
do
	java -Xmx10000m -classpath $FBEVALUATOR_HOME/transgamera-20110622/transgamera.jar eu/himeros/transcoder/TransGamera $FBEVALUATOR_HOME/transgamera-20110622/comb2u.txt $2/$file $3/$file
done

cd $FBEVALUATOR_HOME 
echo "Federizing $3"
echo "$JAVA_PATH/java -Xmx10000m -jar textevaluator.jar $3/"
$JAVA_PATH/java -Xmx10000m -jar textevaluator.jar $3/ 
echo "Done Federizing, now summarizing results in csv file"
cd -
for file in `ls $3/*eval.txt` 
do 
echo -n $file >> $4
echo -n "," >> $4
tail -n 1 $file | cut -c 9- >> $4
done

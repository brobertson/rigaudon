#!/bin/bash
#$ -cwd
#$ -j y
#$ -l h_rt=01:00:00
#$ -l h_vmem=18G
#1. Convert the hocr output to plain text
#2. Evaluate the plain text with Federico's code
#3. Save comma-separated pairs of textfile name and score 
LC_ALL=$LANG
FBEVALUATOR_HOME=/home/fbaumgardt/ocr/bin/fbevaluator
HOCR_OUTPUT=/home/fbaumgardt/ocr/var/texts/septemadthebased00aescuoft/septemadthebased00aescuoft_jp2/2013-07-26-10-20_Kaibel_Round_4_raw_hocr_output
PRIMARY_OUTPUT=/home/fbaumgardt/ocr/var/texts/septemadthebased00aescuoft/septemadthebased00aescuoft_jp2/2013-07-26-10-20_Kaibel_Round_4_txt_output
SECONDARY_OUTPUT=/home/fbaumgardt/ocr/var/texts/septemadthebased00aescuoft/septemadthebased00aescuoft_jp2/2013-07-26-10-20_Kaibel_Round_4_output_tc
CSV_FILE=/home/fbaumgardt/ocr/var/texts/septemadthebased00aescuoft/septemadthebased00aescuoft_jp2/2013-07-26-10-20_Kaibel_Round_4_output_tc/2013-07-26-10-20_Kaibel_Round_4_summary.csv

#usage: lynx_dump.sh $HOCR_OUTPUT $PLAINTEXT_OUTPUT $REGULARIZED_PLAINTEXT_OUTPUT $CSV_FILE
if [[ -z $FBEVALUATOR_HOME ]]; then
  echo '$FBEVALUATOR_HOME not set. Exiting.'
  exit
fi

export JAVA_PATH=/usr/bin
for file in `ls $HOCR_OUTPUT`
do
	TRUNC_FILENAME=$(basename $file)
	TRUNC_FILENAME=${TRUNC_FILENAME%.*}

	echo $TRUNC_FILENAME
	lynx --dump $HOCR_OUTPUT/$file > $PRIMARY_OUTPUT/$TRUNC_FILENAME.txt
done

echo "regularizing files in $PRIMARY_OUTPUT and putting into $SECONDARY_OUTPUT"
for file in `ls $PRIMARY_OUTPUT`
do
	java -Xmx10000m -classpath $FBEVALUATOR_HOME/transgamera-20110622/transgamera.jar eu/himeros/transcoder/TransGamera $FBEVALUATOR_HOME/transgamera-20110622/comb2u.txt $PRIMARY_OUTPUT/$file $SECONDARY_OUTPUT/$file
done

cd $FBEVALUATOR_HOME/textevaluator 
echo "Federizing $SECONDARY_OUTPUT"
echo "$JAVA_PATH/java -Xmx10000m -jar textevaluator.jar $SECONDARY_OUTPUT/"
$JAVA_PATH/java -Xmx10000m -jar textevaluator.jar $SECONDARY_OUTPUT/ 
echo "Done Federizing, now summarizing results in csv file"
cd -

for file in `ls $SECONDARY_OUTPUT/*eval.txt` 
do 
	echo -n $file >> $CSV_FILE
	echo -n "," >> $CSV_FILE
	tail -n 1 $file | cut -c 9- >> $CSV_FILE
done

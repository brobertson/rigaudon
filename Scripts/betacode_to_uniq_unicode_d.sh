#!/bin/bash
if [[ -z $RIGAUDON_HOME ]]; then
  echo '$RIGAUDON_HOME not set. Exiting.'
  exit
fi
basename=$(basename $1)
TMPDIR=/usr/local/OCR_Processing/Dictionary/Temp
preproc_betacode=$TMPDIR/${basename}_beta_no_latin.txt
unicodefile=$TMPDIR/${basename}_unicoded.txt
uniqfile=$TMPDIR/${basename}_uniq.txt
rm $unicodefile
rm $uniqfile
$RIGAUDON_HOME/Scripts/betacode_strip_latin.py $1 > $preproc_betacode
 java -classpath /home/brucerob/Cariboo//lib -jar /usr/local/OCR_Processing/Dictionary/lib/transcoder-1.1-SNAPSHOT.jar -s "$preproc_betacode" -o $unicodefile   -se BetaCode -oe UnicodeD
/home/broberts/rigaudon/Scripts/make_dict.py $unicodefile > $uniqfile 
#rm ${TMPFILE}_unicoded.txt
#rm ${TMPFILE}_uniq.txt


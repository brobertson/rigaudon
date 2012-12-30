#!/bin/bash
basename=$(basename $1)
TMPDIR=/usr/local/OCR_Processing/Dictionary/Temp
preproc_betacode=$TMPDIR/${basename}_beta_no_latin.txt
unicodefile=$TMPDIR/${basename}_unicoded.txt
uniqfile=$TMPDIR/${basename}_uniq.txt
rm $unicodefile
rm $uniqfile
/home/broberts/rigaudon/Scripts/betacode_strip_latin.py $1 > $preproc_betacode
 java -classpath /home/brucerob/Cariboo//lib -jar /usr/local/OCR_Processing/Dictionary/lib/transcoder-1.1-SNAPSHOT.jar -s "$preproc_betacode" -o $unicodefile   -se BetaCode -oe UnicodeD
/home/broberts/rigaudon/Scripts/make_dict.py $unicodefile > $uniqfile 
#rm ${TMPFILE}_unicoded.txt
#rm ${TMPFILE}_uniq.txt


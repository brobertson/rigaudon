#!/bin/bash
#$ -j y
#$ -l h_rt=05:00:00
cp $CSV_FILE $TEXT_SELECTED

#Save info about the process
INFO_FILE=$HOCR_SELECTED/info.txt
python -c "from gamera import __version__
print 'Gamera version: ', __version__
import sys
print ('Python version: %s.%s.%s' % sys.version_info[:3])" > $INFO_FILE
echo -n "OS: " >> $INFO_FILE
uname -sr >> $INFO_FILE
echo -n "Rigaudon build: " >> $INFO_FILE
cd /home/broberts/rigaudon
git rev-parse HEAD >> $INFO_FILE
cd -
#echo $CLASSIFIER_FILE/classifier_glyphs.xml >> $INFO_FILE
md5sum $CLASSIFIER_FILE/classifier_glyphs.xml >> $INFO_FILE
echo $CLASSIFIER_FILE/optimized_settings.xml >> $INFO_FILE
md5sum  $CLASSIFIER_FILE/optimized_settings.xml >> $INFO_FILE
echo -n "Gamera Commands: " >> $INFO_FILE
echo $GAMERA_CMDS >> $INFO_FILE
echo -n "Hocr command: " >> $INFO_FILE
echo $HOCR >> $INFO_FILE
#md5sum $CLASSIFIER_SETTINGS 
#Now report using email.

echo "$BOOK_DIR $DATE done using $filename classifier. `ls $HOCR_SELECTED | wc -l` files created with total score `cat $HOCR_SELECTED/best_scores_sum.txt`." | mutt -s "$BOOK_DIR at sharcnet" -a $GRAPH_IMAGE_FILE -- bruce.g.robertson@gmail.com
#echo "$BOOK_DIR $DATE done" | mail bruce.g.robertson@gmail.com -s "$BOOK_DIR processing"
cd $BOOK_DIR
tar -zcf $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_hocr_and_txt.tar.gz  $RELATIVE_HOCR_SELECTED $RELATIVE_TEXT_SELECTED $RELATIVE_SPELLCHECKED_HOCR_SELECTED $RELATIVE_COMBINED_HOCR
tar -zcf  $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_full.tar.gz $RELATIVE_HOCR_OUTPUT $RELATIVE_PRIMARY_OUTPUT $RELATIVE_SECONDARY_OUTPUT $RELATIVE_HOCR_SELECTED $RELATIVE_TEXT_SELECTED $RELATIVE_SPELLCHECKED_HOCR_SELECTED $RELATIVE_COMBINED_HOCR
cd -
THIS_COMMAND="mkdir /home/brucerob/Rigaudon/${BOOK_NAME}"
ssh heml $THIS_COMMAND
cd $BOOK_DIR
scp -r ${DATE}_${filename}_selected_hocr_output heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r  ${DATE}_${filename}_selected_text_output heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r $RELATIVE_COMBINED_HOCR heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r $RELATIVE_SPELLCHECKED_HOCR_SELECTED heml:/home/brucerob/Rigaudon/${BOOK_NAME}
rm -rf  $HOCR_OUTPUT
rm -rf  $PRIMARY_OUTPUT
rm -rf  $SECONDARY_OUTPUT
rm -rf  $TESS_OUTPUT > /dev/null
rm -rf  $HOCR_SELECTED
rm -rf  $TEXT_SELECTED

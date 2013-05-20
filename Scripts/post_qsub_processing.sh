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
cd $RIGAUDON_HOME 
git rev-parse HEAD >> $INFO_FILE
cd -
md5sum $CLASSIFIER_FILE/classifier_glyphs.xml >> $INFO_FILE
echo $CLASSIFIER_FILE/optimized_settings.xml >> $INFO_FILE
md5sum  $CLASSIFIER_FILE/optimized_settings.xml >> $INFO_FILE
echo -n "Gamera Commands: " >> $INFO_FILE
echo $GAMERA_CMDS >> $INFO_FILE
echo -n "Hocr command: " >> $INFO_FILE
echo $HOCR >> $INFO_FILE
#done saving info about the session

cd $BOOK_DIR

if [ ! -d $JPG_COLOR_IMAGES ]; then
 mkdir $JPG_COLOR_IMAGES
for image_file in `ls *jp2 *tiff *png`
  do 
    convert -quality 30 -depth 8 $image_file  $JPG_COLOR_IMAGES/${image_file%.*}.jpg
  done
  scp -r $JPG_COLOR_IMAGES heml:/home/brucerob/Rigaudon/Images/Color
fi

echo "done making color images; doing gray"
if [ ! -d $JPG_GRAY_IMAGES ]; then
mkdir $JPG_GRAY_IMAGES
for image_file in `ls *jp2 *tiff`
  do
  convert -colorspace Gray -quality 30 -depth 8  $JPG_GRAY_IMAGES/${image_file%.*}.jpg
  done
  scp -r $JPG_GRAY_IMAGES heml:/home/brucerob/Rigaudon/Images/Gray
fi

echo "done  making gray images; now making sidebyside view. My pwd is:"
pwd 

HOCR_DIR_FOR_SIDE_VIEW=$RELATIVE_SPELLCHECKED_HOCR_SELECTED

if [ $MIX_HOCR = "True" ]
then
  HOCR_DIR_FOR_SIDE_VIEW=$RELATIVE_COMBINED_HOCR
fi 

python $RIGAUDON_HOME/Scripts/make_sidebyside_view.py $HOCR_DIR_FOR_SIDE_VIEW/  $SIDE_BY_SIDE_VIEW

tar -zcf $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_hocr_and_txt.tar.gz  $RELATIVE_HOCR_SELECTED $RELATIVE_TEXT_SELECTED $RELATIVE_SPELLCHECKED_HOCR_SELECTED $RELATIVE_COMBINED_HOCR
tar -zcf  $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_full.tar.gz $RELATIVE_HOCR_OUTPUT $RELATIVE_PRIMARY_OUTPUT $RELATIVE_SECONDARY_OUTPUT $RELATIVE_HOCR_SELECTED $RELATIVE_TEXT_SELECTED $RELATIVE_SPELLCHECKED_HOCR_SELECTED $RELATIVE_COMBINED_HOCR $RELATIVE_HOCR_BLENDED $RELATIVE_TEXT_BLENDED
cd -
THIS_COMMAND="mkdir /home/brucerob/Rigaudon/${BOOK_NAME}"
ssh heml $THIS_COMMAND > /dev/null
cd $BOOK_DIR

scp -r ${DATE}_${filename}_selected_hocr_output heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r ${DATE}_${filename}_selected_text_output heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r $RELATIVE_COMBINED_HOCR heml:/home/brucerob/Rigaudon/${BOOK_NAME}
scp -r $RELATIVE_SPELLCHECKED_HOCR_SELECTED heml:/home/brucerob/Rigaudon/${BOOK_NAME}

scp -r $SIDE_BY_SIDE_VIEW heml:/home/brucerob/Rigaudon/Views/SideBySide
scp  $BOOK_DIR/robertson_${DATE}_${BOOK_NAME}_${filename}_full.tar.gz heml:/home/brucerob/Rigaudon/Inbox

echo "$BOOK_DIR $DATE done using $filename classifier. `ls $HOCR_SELECTED | wc -l` files created with total score `cat $HOCR_SELECTED/best_scores_sum.txt`. Materials at http://heml.mta.ca/Rigaudon/Views/SideBySide/${RELATIVE_SIDE_BY_SIDE_VIEW} `cat $INFO_FILE`" | mutt -s "$BOOK_DIR at sharcnet" -a $GRAPH_IMAGE_FILE $GRAPH_IMAGE_FILE_3D -- bruce.g.robertson@gmail.com

rm -rf  $HOCR_OUTPUT
rm -rf  $PRIMARY_OUTPUT
rm -rf  $SECONDARY_OUTPUT
rm -rf  $TESS_OUTPUT > /dev/null
rm -rf  $HOCR_SELECTED
rm -rf  $TEXT_SELECTED




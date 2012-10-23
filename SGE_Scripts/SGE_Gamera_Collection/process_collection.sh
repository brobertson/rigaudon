

#set the directory of the collection of books
#COLLECTION_DIR=/usr/local/OCR_Processing/Texts/Athenaeus/Pngs
# We expect two args: the collection_dir and the classifier_dir
USAGE_MESSAGE="Usage: process_collection collection_dir [classifier_dir]"
EXPECTED_ARGS_MIN=1
EXPECTED_ARGS_MAX=2
E_BADARGS=65

if [ $# -lt $EXPECTED_ARGS_MIN -o $# -gt $EXPECTED_ARGS_MAX ]
then
  echo $USAGE_MESSAGE
  exit $E_BADARGS
fi

COLLECTION_DIR=$1
CLASSIFIER_DIR=$2

if [ ! -d $COLLECTION_DIR ]; then
	echo $USAGE_MESSAGE
	exit $E_BADARGS
fi


OUTPUT_DIR=/tmp/sge_out
ERROR_DIR=/tmp/sge_errors


if [ ! -d $OUTPUT_DIR ] 
then
  mkdir $OUTPUT_DIR
fi

if [ ! -d $ERROR_DIR ]
then 
  mkdir $ERROR_DIR
fi


#This makes a 'filelist.txt' file for each book, that is, 
#directory within COLLECTION_DIR

#In particular, these are all the 'png' files found therein
#TODO: add tiff, too, and perhaps 'PNG' and other plausible
#variants
echo "Processing all book files in $COLLECTION_DIR ..."
for BOOK_DIR in `find -L $COLLECTION_DIR/* -maxdepth 0 -type d`
do
echo ""
echo -e "\t Counting the number of pages in $COLLECTION_DIR/$BOOK_DIR..."
FILE_LIST=$BOOK_DIR/filelist.txt
find -L $BOOK_DIR/* -maxdepth 0 -type f -name '*png' -print | sort > $FILE_LIST

#This counts the number of files, necessary to provide
#an arbitrary number of jobs
export FILE_COUNT=`cat $FILE_LIST | wc -l`
echo -e "\t\tFound $FILE_COUNT ..."
#do error check on 0 pages
if [ ! $FILE_COUNT -gt 0 ]; then
  echo -e "\t****ERROR: there are no usable pages in directory $BOOK_DIR"
  echo -e "\tThis book will not be processed."
  continue
fi

if [ -z "$CLASSIFIER_DIR" ]; then
	CLASSIFIER_FILE=`cat $BOOK_DIR/classifier.txt`
else
	CLASSIFIER_FILE=$CLASSIFIER_DIR
fi

#error checking before we commit to processing the books
if  [ ! -d $CLASSIFIER_FILE ]; then
	echo -e "\t****ERROR: There is no classifier.txt file in book $BOOK_DIR"
	echo -e "\tand you haven't specified any classifier on the command line."
	echo -e "\tThis book will not be processed."
	continue
fi

echo -e "\tClassifier for $BOOK_DIR: $CLASSIFIER_FILE"

if [ ! -f "$CLASSIFIER_FILE/classifier_glyphs.xml" ]; then
	echo -e "\t***ERROR: This classifier directory does not have a glyphs file."
	echo -e "\tThe book $BOOK_DIR will not be processed."
	continue
fi

if [ ! -f "$CLASSIFIER_FILE/optimized_settings.xml" ]; then
        echo -e "\t****ERROR: This classifier directory does not have an optimized_settings file."
        echo -e "\tThe book $BOOK_DIR will not be processed."
        continue
fi

filename=$(basename $CLASSIFIER_FILE) 
filename=${filename%.*}  
DATE=`date +%F-%T`
DATE=$DATE OUTPUT_DIR=$OUTPUT_DIR ERROR_DIR=$ERROR_DIR BOOK_DIR=$BOOK_DIR FILE_LIST=$FILE_LIST FILE_COUNT=$FILE_COUNT CONDITIONS=testing CLASSIFIER_FILE=$CLASSIFIER_FILE bash ./book_loop.sh & #/home/broberts/${filename}.btxt &
done

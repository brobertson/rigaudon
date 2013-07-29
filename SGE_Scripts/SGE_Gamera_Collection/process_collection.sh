#!/bin/bash

#set the directory of the collection of books
#COLLECTION_DIR=/usr/local/OCR_Processing/Texts/Athenaeus/Pngs
# We expect two args: the collection_dir and the classifier_dir
USAGE_MESSAGE="Usage: process_collection collection_dir [classifier_dir]"
EXPECTED_ARGS_MIN=1
EXPECTED_ARGS_MAX=2
E_BADARGS=65
COLLECTION_DIR=$1
CLASSIFIER_DIR=$2
#If the GAMERA_CMDS variable is not set, give it the default
#value
export GAMERA_CMDS=${GAMERA_CMDS:-$DEFAULT_GAMERA_CMDS}
#export ${GAMERA_CMDS:=$DEFAULT_GAMERA_CMDS}
echo "Gamera commands: $GAMERA_CMDS"
#If the HOCR variable is not set, then set it to 'N'
export ${HOCR:="N"}
#If the DRIVER_HOCR_IS_LATINSCRIPT variable is not set, then set it to 'N'
#export ${DRIVER_HOCR_IS_LATINSCRIPT:="False"}
#If the MIX_HOR variable is not set, then set it to TRUE; this is default behaviour
#but overridden if other OCR is seen to be Greek script
export ${MIX_HOCR:="True"}



if [ $# -lt $EXPECTED_ARGS_MIN -o $# -gt $EXPECTED_ARGS_MAX ]
then
  echo $USAGE_MESSAGE
  exit $E_BADARGS
fi
if [ ! -d $COLLECTION_DIR ]; then
	echo $USAGE_MESSAGE
	exit $E_BADARGS
fi

#Check the directories for the outputs of Sun Grid Engine
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

#In particular, these are all the 'jp2' files found therein
#TODO: add tiff, too, and perhaps 'PNG' and other plausible
#variants
echo "Processing all book files in $COLLECTION_DIR ..."
export PREVIOUS_BOOK_NAME=""
for BOOK_DIR in `find -L $COLLECTION_DIR/* -maxdepth 0 -type d`
do
	echo -e "\n\t Counting the number of pages in $COLLECTION_DIR/$BOOK_DIR..."
	export FILE_LIST=$BOOK_DIR/filelist.txt
	find -L $BOOK_DIR/* -maxdepth 0 -type f  -regextype posix-extended -regex '.*\.(png|jp2|tiff|tif)' -print | sort > $FILE_LIST
	#This counts the number of files, necessary to provide
	#an arbitrary number of jobs
	export FILE_COUNT=`cat $FILE_LIST | wc -l`
	echo -e "\t\tFound $FILE_COUNT ..."
	#do error check on 0 pages
	if [ ! $FILE_COUNT -gt 0 ]; then
	  echo -e "\t****ERROR: there are no usable pages in directory $BOOK_DIR \n\tThis book will not be processed."
	  continue
	fi
	if [ -z "$CLASSIFIER_DIR" ]; then
		export CLASSIFIER_FILE=`cat $BOOK_DIR/classifier.txt`
	else
		export CLASSIFIER_FILE=$CLASSIFIER_DIR
	fi
	#error checking before we commit to processing the books
	if  [ ! -d $CLASSIFIER_FILE ]; then
		echo -e "\t****ERROR: There is no classifier.txt file in book $BOOK_DIR \n\tand you haven't specified any classifier on the command line. \n\tThis book will not be processed."
		continue
	fi
	echo -e "\tClassifier for $BOOK_DIR: $CLASSIFIER_FILE"
	if [ ! -f "$CLASSIFIER_FILE/classifier_glyphs.xml" ]; then
		echo -e "\t***ERROR: This classifier directory does not have a glyphs file. \n\tThe book $BOOK_DIR will not be processed."
		continue
	fi
	if [ ! -f "$CLASSIFIER_FILE/optimized_settings.xml" ]; then
	        echo -e "\t****ERROR: This classifier directory does not have an optimized_settings file. \n\tThe book $BOOK_DIR will not be processed."
	        continue
	fi

	export DATE=`date +%F-%H-%M`
	export BOOK_DIR
	BOOK_NAME=$(basename $BOOK_DIR)
	echo "bookname: $BOOK_NAME"
	export BOOK_NAME
	bash $RIGAUDON_HOME/SGE_Scripts/SGE_Gamera_Collection/book_loop.sh
	export PREVIOUS_BOOK_NAME=$BOOK_NAME
done

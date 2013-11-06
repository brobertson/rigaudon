#!/bin/bash -e
usage(){
	echo "Usage: $0 -l classifier_model -o output_filename [-v -p] input_filename"
	echo "-v verbose output"
	echo "-p Image has already been processed, useful for paralleling output"
	exit 1
}

delete_string=" &> /dev/null "
verbose=false
image_is_preprocessed=""
columns_command=""
#Get the args
while getopts ":l:o:C:c:vp" opt; do
  case $opt in
    v)
	    delete_string=""
	    verbose=true
	 ;;
    p)
	    image_is_preprocessed=true
	    ;;
    o)
     output_filename=$OPTARG
     ;;
    c)
	    columns_command="--maxcolseps $OPTARG"
	    ;;
    l)
      classifier=$OPTARG
      if [ ! -f $classifier ]; then
      echo "Model file $classifier does not exist"
      usage
      fi
      model_command='-m '$classifier
      if  $verbose ; then
	      echo using model $classifier
      fi
      ;;
     C)
      compare_file=$OPTARG
      if [ ! -f $compare_file ]; then
      echo "comparand file $compare_file does not exist"
      usage
      fi
      compare_command=' -C '$compare_file
      if $verbose ; then
      	echo using comparand $compare_file
      fi
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      ;;
  esac
done

#Test the args 
shift $(($OPTIND - 1))
if [ ! $# -gt 0 ]; then 
	echo "no filename given"
	usage	
fi

if $verbose ; then
	echo "outputfile $output_filename"
fi

if [ -z  $output_filename ]; then
	echo "Output file $output_filename not set"
	usage
fi

#check that $OCROPUS_HOME is set
if [[ -z "$OCROPUS_HOME" ]]; then
	echo "Please set \$OCROPUS_HOME"
	exit 1
fi

#extend the variable
OCROPUS_BIN=$OCROPUS_HOME/ocropus/ocropy/


fbname=`basename "$1"`
if $verbose ; then
	echo $fbname
fi

barefilename=${fbname%.*}
extension="${fbname##*.}"
if $verbose ; then
echo $barefilename
fi
process_dir=/tmp/$barefilename
process_file=$1
#echo preprocessed? $image_is_preprocessed
if [[ ! -d $process_dir ]]; then
echo about to make $process_dir
mkdir $process_dir
if [ "$extension" != "png" ]
then
echo "converting $1 to $process_dir/$barefilename.png"
eval convert $1 $process_dir/$barefilename.png $delete_string
process_file=$process_dir/$barefilename.png
fi

if [[ -z "$fbname" ]]; then
	usage
	exit 1
fi

eval $OCROPUS_BIN/ocropus-nlbin $process_file  -o $process_dir $delete_string
eval $OCROPUS_BIN/ocropus-gpageseg $columns_command  $process_dir'/????.bin.png' #$delete_string
#end condition of process_dir existing
fi
process_dir_for_classifier=`mktemp -d`
cp -a $process_dir/* $process_dir_for_classifier 
eval $OCROPUS_BIN/ocropus-rpred   $model_command $process_dir_for_classifier'/????/??????.bin.png' $delete_string
eval $OCROPUS_BIN/ocropus-hocr $process_dir_for_classifier'/????.bin.png' -o $output_filename $delete_string
#rm -rf $process_dir_for_classifier > /dev/null
#ocropus-visualize-results temp


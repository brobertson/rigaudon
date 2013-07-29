#!/bin/bash
export LC_ALL=$LANG
export HOCR="ABBYY" 
export RIGAUDON_HOME=/home/fbaumgardt/ocr/bin/rigaudon
export FBEVALUATOR_HOME=/home/fbaumgardt/ocr/bin/fbevaluator
export GAMERA_CMDS_DEFAULT=" --split --autogroup  --filter --otsu  0.94,0.97,1.0,1.03,1.05,1.07,1.09,1.12,1.15,1.17"
# export GAMERA_CMDS_DEFAULT=" --split --autogroup  --filter --otsu  0.69,0.72,0.75,0.78,0.81,0.84,0.87,0.91,0.94,0.97,1.0,1.03,1.05,1.07,1.09,1.12,1.15,1.17,1.19,1.22"
export GAMERA_CMDS=" --split --autogroup  --filter --otsu  0.94,0.97,1.0,1.03,1.05,1.07,1.09,1.12,1.15,1.17"
export ARCHIVE_ID=septemadthebased00aescuoft
export CLASSIFIER_DIR=ocr/bin/rigaudon/Gamera/Classifiers/Kaibel_Round_4/
export TEXT_STAGING_DIR=/home/fbaumgardt/ocr/var/texts

export PROCESSING_DIR=$TEXT_STAGING_DIR/$ARCHIVE_ID

#Set the directories for the outputs of Sun Grid Engine
export OUTPUT_DIR=/home/fbaumgardt/ocr/var/logs
export ERROR_DIR=/home/fbaumgardt/ocr/var/logs

ocr/bin/rigaudon/Scripts/process_volume_from_archive.sh
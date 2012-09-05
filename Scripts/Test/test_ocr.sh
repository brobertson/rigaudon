GREEKOCR_PATH=/home/broberts/python/bin
python  $GREEKOCR_PATH/greekocr4gamera.py -x Gamera_Oxford_optimized_classifier.xml  --filter --deskew --split --autogroup -s -u output- AhcOAAAAYAAJ-00000018.png
diff correct-output.txt output-AhcOAAAAYAAJ-00000018.txt
rm output-AhcOAAAAYAAJ-00000018.txt

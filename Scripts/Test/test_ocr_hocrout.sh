python  $GREEKOCR_PATH/greekocr4gamera.py -x Gamera_Oxford_optimized_classifier.xml --filter  --deskew  --split --autogroup -s --hocrout -u output- AhcOAAAAYAAJ-00000018.png
#python -V >>  output-AhcOAAAAYAAJ-00000018.txt
python -c "from gamera import __version__
print 'Gamera version: ', __version__
import sys
print ('The Python version is %s.%s.%s' % sys.version_info[:3])" >>  output-AhcOAAAAYAAJ-00000018.txt
#diff correct-output.txt output-AhcOAAAAYAAJ-00000018.txt
#rm output-AhcOAAAAYAAJ-00000018.txt

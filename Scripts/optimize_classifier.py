#!/usr/bin/python
import sys, os
file_in = sys.argv[1]
file_out = os.path.join(os.path.dirname(sys.argv[1]),"optimized_classifier.xml")
from gamera.core import init_gamera
init_gamera()
from gamera.knn import kNNInteractive
classifier = kNNInteractive()
classifier.from_xml_filename(file_in)
from gamera.knn_editing import edit_mnn_cnn
editedClassifier = edit_mnn_cnn(classifier)
editedClassifier.to_xml_filename(file_out)

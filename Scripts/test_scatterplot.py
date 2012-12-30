#!/usr/bin/python
import matplotlib
matplotlib.use('Agg')
import sys
import os.path
import shutil
from operator import itemgetter
import numpy as np
from pylab import *
summary_file = sys.argv[1]
graph_image_file=sys.argv[2]
summary = open(summary_file)
scatterplot_data = []
dictionary = {}
image_type_dictionary = {}

for line in summary:
	[text_line,bValue] = line.split(',')
        text_line = os.path.split(text_line)[1]
	#print "text_line is: ", text_line
	[text_name,page_number,file_type,junk,thresh] = text_line.split('_')
	[thresh_good,junk] = thresh.split('-')
	thresh_good = int(thresh_good)
	image_type_dictionary[page_number] = file_type
	try:
		pairs = dictionary[page_number]
		pairs.append([thresh_good,float(bValue)])
	except KeyError:
		dictionary[page_number] = [[thresh_good,float(bValue)]]
	scatterplot_data.append([thresh_good,float(bValue)])



#now copy them from the source file to the target directory
#now pass best_scores through gnuplot

foo = np.array(scatterplot_data)
plot(foo[:,0],foo[:,1],'o')
savefig(graph_image_file)

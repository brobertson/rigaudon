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
hocr_in_directory=sys.argv[2]
txt_in_directory=sys.argv[3]
hocr_out_directory=sys.argv[4]
txt_out_directory=sys.argv[5]

summary = open(summary_file)

dictionary = {}


for line in summary:
	[text_line,bValue] = line.split(',')
        text_line = os.path.split(text_line)[1]
	print "text_line is: ", text_line
	[text_name,page_number,file_type,junk,thresh] = text_line.split('_')
	
	[thresh_good,junk] = thresh.split('-')
	thresh_good = int(thresh_good)

	try:
		pairs = dictionary[page_number]
		pairs.append([thresh_good,float(bValue)])
	except KeyError:
		dictionary[page_number] = [[thresh_good,float(bValue)]]

#This makes a 3-d graph of all the results
#needs matplotlib version => 1.0
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#verts = []
#x = 0
#for key in sorted(dictionary.keys()):
#	values = dictionary[key]
#	values = sorted(values, key=itemgetter(0))
#	x = x + 1
#	threed = ""
#	for pair in values: 
#		threed += str(x) + " " + str(pair[0]) + " " + str(pair[1]) + "\n"
#		verts.append([pair[0],pair[1]])
#poly = PolyCollection(verts)
#poly.set_alpha(0.7)
#ax.add_collection3d(poly, zs = range[0:x], zdir = 'z')
#plt.show()

# now pass threed through gnuplot

page_bscores = []
for key in dictionary.keys():
	values = dictionary[key]
	out_values = sorted(values, key=itemgetter(1))
	[best_thresh,best_bScore] = out_values[-1]
	page_bscores.append([key,best_bScore])
        best_file = text_name + "_" + key + "_" + file_type + "_thresh_" + str(best_thresh)
        best_txt_file = best_file + ".txt"
        best_html_file = best_file + ".html"
        print best_txt_file
        shutil.copy(os.path.join(hocr_in_directory, best_html_file), os.path.join(hocr_out_directory, best_html_file))
        shutil.copy(os.path.join(txt_in_directory, best_txt_file), os.path.join(txt_out_directory, best_txt_file))
page_bscores = sorted(page_bscores, key=itemgetter(1))
page_bscores_sorted = sorted(page_bscores, key=itemgetter(0))

print page_bscores
best_scores = ""
#now copy them from the source file to the target directory
#now pass best_scores through gnuplot
page_bscores_np = np.array(page_bscores_sorted)
plot(page_bscores_np[:,0],page_bscores_np[:,1])
savefig(os.path.join(hocr_out_directory,"page_quality.png"))

	

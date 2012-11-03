#!/usr/bin/python
import sys
from operator import itemgetter

summary_file = sys.argv[1]
hocr_in_directory=sys.argv[2]
txt_in_directory=sys.argv[3]
hocr_out_directory=sys.argv[4]
txt_out_directory=sys.argv[5]

summary = open(summary_file)

dictionary = {}

for line in summary:
	[text_line,bValue] = line.split(',')
	[text_name,page_number,file_type,junk,thresh] = text_line.split('_')
	
	[thresh_good,junk] = thresh.split('-')
	thresh_good = int(thresh_good)

	try:
		pairs = dictionary[page_number]
		pairs.append([thresh_good,float(bValue)])
	except KeyError:
		dictionary[page_number] = [[thresh_good,float(bValue)]]

#This makes a 3-d graph of all the results
x = 0
for key in sorted(dictionary.keys()):
	values = dictionary[key]
	values = sorted(values, key=itemgetter(0))
	x = x + 1
	threed = ""
	for pair in values: 
		threed += str(x) + " " + str(pair[0]) + " " + str(pair[1]) + "\n"
# now pass threed through gnuplot

page_bscores = []
for key in dictionary.keys():
	values = dictionary[key]
	out_values = sorted(values, key=itemgetter(1))
	[best_thresh,best_bScore] = out_values[-1]
	page_bscores.append([key,best_bScore])
	page_bscores = sorted(page_bscores, key=itemgetter(1))


best_scores = ""
for item in page_bscores:
	best_scores += item[0] + " " + str(item[1]) + "\n"
	best_file = best_txt_file = text_name + "_" + key + "_" + file_type + "_thresh_" + str(best_thresh)
	best_txt_file = best_file + ".txt"
	best_html_file = best_file + ".html"
	#now copy them from the source file to the target directory

#now pass best_scores through gnuplot
	
	
	

	

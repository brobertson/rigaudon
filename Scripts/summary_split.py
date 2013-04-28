#!/usr/bin/python
import matplotlib
matplotlib.use('Agg')
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.collections import PolyCollection
# import matplotlib.pyplot as plt
# import sys
# import os.path
# import shutil
# from operator import itemgetter
# import numpy as np
# from matplotlib.colors import colorConverter
# from pylab import *

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import numpy as np
import sys
import os.path
import os
import shutil
from operator import itemgetter

# import pylab as plab

# from pylab import plot
summary_file = sys.argv[1]
hocr_in_directory = sys.argv[2]
txt_in_directory = sys.argv[3]
hocr_out_directory = sys.argv[4]
txt_out_directory = sys.argv[5]
graph_image_file = sys.argv[6]
try:
    volume_id = sys.argv[7]
except:
    volume_id = ""
try:
    classifier_name = sys.argv[8]
except:
    classifier_name = ""

summary = open(summary_file)

dictionary = {}
image_type_dictionary = {}

for line in summary:
    [text_line, bValue] = line.split(',')
    text_line = os.path.split(text_line)[1]
    print "text_line is: ", text_line
    try:
        [text_name, page_number, file_type,
            junk, thresh] = text_line.split('_')
        [thresh_good, junk] = thresh.split('-')
        thresh_good = int(thresh_good)
    except ValueError:
        print "got a value error for first run"
        [text_name, page_number, file_type, junk] = text_line.split('_')
        thresh_good = -1
    image_type_dictionary[page_number] = file_type
    try:
        pairs = dictionary[page_number]
        pairs.append([thresh_good, float(bValue)])
    except KeyError:
        print "got a key error"
        dictionary[page_number] = [[thresh_good, float(bValue)]]

# This makes a 3-d graph of all the results
# needs matplotlib version => 1.0
fig = plt.figure()
ax = fig.gca(projection='3d')
cc = lambda arg: colorConverter.to_rgba(arg, alpha=0.1)
verts = []
x = 0
threed = ""
max_b_score = 0
max_threshold = 0
min_threshold = 255
for key in sorted(dictionary.keys()):
    this_image = []
    values = dictionary[key]
    values = sorted(values, key=itemgetter(0))
    x = x + 1
    for pair in values:
        threed += str(x) + " " + str(key) + " " + str(
            pair[0]) + " " + str(pair[1]) + "\n"
        this_image.append((pair[0], pair[1]))
        if pair[1] > max_b_score:
            max_b_score = pair[1]
        if pair[0] > max_threshold:
            max_threshold = pair[0]
        if pair[0] < min_threshold:
            min_threshold = pair[0]
    this_image.insert(0, (this_image[0][0] - 1, 0))
    this_image.append((this_image[-1][0] + 1, 0))
    verts.append(this_image)

blueish = colorConverter.to_rgba('b', alpha=0.5)
# print verts
poly = PolyCollection(verts, closed=False, edgecolors=[
                      blueish], linewidths=[1], facecolors=[cc('y')])

# poly.set_alpha(0.1)
ax.add_collection3d(poly, zs=range(0, x), zdir='y')

ax.set_xlabel('Binarization threshold')
ax.set_xlim3d(min_threshold, max_threshold)
ax.set_ylabel('Page number')
ax.set_ylim3d(-1, len(verts))
ax.set_zlabel('B-score')

graph_title = volume_id + " " + classifier_name + \
    '\n'+os.getenv('GAMERA_CMDS', '[no gamera cmds]')
ax.set_title(graph_title, fontsize="xx-small")
ax.set_zlim3d(0, max_b_score)
fig.savefig(os.path.join(hocr_out_directory, "3d.png"))

# now make 3d scores file
td_scores_file = open(os.path.join(hocr_out_directory, "3d_scores.txt"), 'w+')
td_scores_file.write(threed)
# now pass threed through gnuplot
best_bscore_sum = 0
page_bscores = []
for key in dictionary.keys():
    values = dictionary[key]
    file_type = image_type_dictionary[key]
    out_values = sorted(values, key=itemgetter(1))
    [best_thresh, best_bScore] = out_values[-1]
    best_bscore_sum += best_bScore
    page_bscores.append([key, best_bScore])
    thresh_string = "_thresh_" + str(best_thresh)
    # in the case that the input file is onebit, we use a thresh of -1 as a
    # magic number
    if best_thresh < 0:
        thresh_string = "_onebit"
    best_file = text_name + "_" + key + "_" + file_type + thresh_string
    best_txt_file = best_file + ".txt"
    best_html_file = best_file + ".html"
    # print best_txt_file
    shutil.copy(os.path.join(hocr_in_directory, best_html_file), os.path.join(
        hocr_out_directory, best_html_file))
    shutil.copy(os.path.join(txt_in_directory, best_txt_file), os.path.join(
        txt_out_directory, best_txt_file))
page_bscores = sorted(page_bscores, key=itemgetter(1))
page_bscores_sorted = sorted(page_bscores, key=itemgetter(0))

best_bscore_sum_file = open(os.path.join(
    hocr_out_directory, "best_scores_sum.txt"), 'w+')
best_bscore_sum_file.write(str(best_bscore_sum))
best_scores_file = open(os.path.join(
    hocr_out_directory, "best_scores.txt"), 'w+')
import pprint
pp = pprint.PrettyPrinter(indent=4)
out = pp.pformat(page_bscores)
best_scores_file.write(out)


best_scores = ""
# now copy them from the source file to the target directory
# now pass best_scores through gnuplot
# needs matplotlib version => 1.0


fig2 = plt.figure()
page_bscores_np = np.array(page_bscores_sorted)
plt.ylim(0, 0.75)
plt.plot(page_bscores_np[:, 0], page_bscores_np[:, 1])
plt.title(graph_title, fontsize="xx-small")

plt.savefig(graph_image_file)

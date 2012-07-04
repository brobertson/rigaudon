# Copyright (C) 2011 Emily Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 

import os
import time
from gamera.core import *

init_gamera()
from gamera.plugin import *
from gamera.toolkits.ocr.classes import Page
#create a directory to store the partial images in
if not os.path.exists("/home/ubuntu/Desktop/temp/"):
    os.makedirs("/home/ubuntu/Desktop/temp/")
#load the image
image = load_image(r"00000129.png")
image = image.to_onebit()
#first segmentation algorithm 
class StepOne(Page):
    def page_to_lines(self):
        self.ccs_lines = self.img.bbox_merging(2,7)
#second segmentation algorithm
class StepTwo(Page):
	def page_to_lines(self):
		self.ccs_lines = self.img.runlength_smearing(0,1,0)

result = StepOne(image)
result.segment()
boxes = result.ccs_lines

lent = len(boxes)
t = time.time()
upper_leftx = [None]*lent
upper_lefty = [None]*lent
lower_rightx= [None]*lent
lower_righty= [None]*lent

i = 0
for box in boxes:
	#get the bounding box coordinates for each box
	upper_leftx[i] = box.ul_x
	upper_lefty[i] = box.ul_y
	lower_rightx[i] = box.lr_x
	lower_righty[i] = box.lr_y
	name =  "/home/ubuntu/Desktop/temp/" + str(i) + "-" +  str(t) + ".png"
	im = box.image_copy()
	im.reset_onebit_image()
	im.save_PNG(name)	
	i=i+1
k = 0
while k < i:
	#draw the boxes
	image.draw_hollow_rect((upper_leftx[k],upper_lefty[k]), (lower_rightx[k],lower_righty[k]), 1, 2)
	name1 = "/home/ubuntu/Desktop/temp/" + str(k) + "-" +str(t)+  ".png"
	#load the partial image	
	image2 = load_image(name1)
	image2 = image2.to_onebit()
	result2 = StepTwo(image2)
	result2.segment()
	words = []	
	for line in result2.textlines:
		for word in line.words:
			words.append(word)

	if(len(words) > 0):
		for word in words:
			ul_xs = word[0].ul_x
			ul_ys = word[0].ul_y
			lr_xs = word[0].lr_x
			lr_ys = word[0].lr_y
			
			for letter in word:
				#find the lowest upper left coordinates, and the highest lower right coordinates
				if(ul_xs > letter.ul_x):
					ul_xs = letter.ul_x	
				if(ul_ys > letter.ul_y):
					ul_ys = letter.ul_y
				if(lr_xs < letter.lr_x):
					lr_xs = letter.lr_x
				if(lr_ys < letter.lr_y):
					lr_ys = letter.lr_y
			#draw the word boxes
			image.draw_hollow_rect((upper_leftx[k]+ul_xs -1,upper_lefty[k]+ul_ys -1),(upper_leftx[k]+lr_xs +1 ,upper_lefty[k]+lr_ys +1 ), 1, 2)
	k = k+1
#save the image
image.save_PNG("out-" + str(t) + ".png")

#!/usr/bin/python
# coding: utf-8

import sys
import string

with open(sys.argv[1],'r') as f:
	for x in f:
		for word in string.split(x):
			print word


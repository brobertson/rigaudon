#!/bin/bash
convert -colorspace Gray -quality 30 -depth 8 $1 pbm:- |convert pbm:- $2

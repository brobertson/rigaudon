import unicodedata as ud
import os, glob, sys
import codecs

path = sys.argv[1]
path_out = os.path.join(path, 'Output_normalized')
path_debug = os.path.join(path, 'Output_normalization_debug')
print path_out
try:
	os.mkdir(path_out)
	os.mkdir(path_debug)
except OSError:
	pass

for infile in glob.glob(os.path.join(path, "*txt")):
	file_out = os.path.join(path_out, os.path.basename(infile))
	file_debug = os.path.join(path_debug, os.path.basename(infile))
	print "converting " + infile + " to " + file_out
	fi = codecs.open(infile,'r','utf-8')
	fo = codecs.open(file_out,'w','utf-8')
	fd = codecs.open(file_debug,'w','utf-8')
	for line in fi:
		normalized_line = ud.normalize('NFC',line)
		fo.write(normalized_line)
		fd.write(normalized_line)
		for char in normalized_line.rstrip():
			fd.write(ud.name(char))
			fd.write('\n')

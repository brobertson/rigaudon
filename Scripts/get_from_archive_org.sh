#!/bin/bash
#usage get_from_archive.sh filename

# Takes a file comprising a list of archive.org identities, and downloads the corresponding
# image zip file, meta.xml and abbyy.gz files
# It tries first to get a _jp2.zip file, but if that isn't possible, it assumes _tif.zip

for fileIn in `cat $1`
do
file=`basename $fileIn`
echo "Doing $file..."
curl -IL "http://www.archive.org/download/$file/${file}_jp2.zip" | tee  /tmp/response.txt 
grep HTTP/1.1 /tmp/response.txt | tail -1 | grep 404
#curl -OL -f  http://www.archive.org/download/$file/${file}_jp2.zip
badDL=$?
echo "status: $badDL"
if [ "$badDL" -eq "0" ]; then
  #the jp2 archive is not available, so we'll guess that it's tiff
  wget http://www.archive.org/download/$file/${file}_tif.zip
else
  wget  http://www.archive.org/download/$file/${file}_jp2.zip
fi
wget http://www.archive.org/download/$file/${file}_meta.xml
sleep 20
wget http://www.archive.org/download/$file/${file}_abbyy.gz
done

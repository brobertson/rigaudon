BASE=http://commondatastorage.googleapis.com/books/ancient-greek-and-latin-20100511/
while read line; do
  zipfile=$line.zip
  echo $BASE$zipfile
  wget $BASE$zipfile
  unzip $zipfile
done < $1 


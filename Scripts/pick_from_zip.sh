for archive in "$@"
do
array=($(unzip -qq -l "$archive" | awk '{print $4}'|grep png | sort))
 #for str in ${array[@]}; do
    #   echo "$str"
 #  done
 for i in ${array[@]}; 
do echo "$RANDOM $i"; 
done | sort | sed -r 's/^[0-9]+ //' | head > ~/out.txt

for i in `cat ~/out.txt`
do 
  unzip $archive $i
done 
done

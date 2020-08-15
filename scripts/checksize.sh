#! /bin/bash

#find . -type f -exec bash -c ~/checksize.sh ;
echo ${@}
if [ -z "$1" ]
then
    echo "\$1 empty" >&2
    exit
fi

size=($(identify -format "%w %h" "$1" | tr -d "()"))
#echo ${size[@]}
#echo ${size[0]}
#echo ${size[1]}
if [ ${size[0]} -lt 160 -a ${size[1]} -lt 120 ]
then
    #rm -v "$1"
    echo $1
fi


for i
do
    size=($(identify -format "%w %h" "$i"))
    (( size[1] < 161 || size[2] < 121 )) && rm -v "$i"
done


#find . -name "*.bak" -type f -delete
#find . -iname "*.jpg" -type f | xargs -I{} identify -format '%w %h %i' {} | awk '$1<160 || $2<120'


find . -iname "*.jpg" -type f -exec identify -format '%i %wx%h\n' '{}' \; | grep 160x120


-exec <command> '{}' \;

find . -iname "*.jpg" -type f | xargs -I{} identify -format '\n%w %h %i' {} | awk '$1<161 || $2<121' | cut -d' ' -f3 | xargs rm

find . -iname "*.jpg" -type f | xargs bash -c 'for i; do size=($(identify -format "%w %h" "$i")); (( size[1] < 161 || size[2] < 121 )) && echo "$i"'
find . -iname "*.jpg" -type f -exec bash -c 'for i; do size=($(identify -format "%w %h" "$i")); (( size[1] < 161 || size[2] < 121 )) && rm -v "$i"' remove-files {} +
find . -iname "*.jpg" -type f | xargs -I{} identify -format '%w %h %i' {} | awk '$1<160 || $2<120'

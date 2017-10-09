#!/bin/bash

for filename in preprocessing/articles/*; do
    #awk print '{print /$QUERY/}' $filename > output.txt
    awk '/cat\s{1,5}was/ {
        for(i=1;i<=NF;++i)
            if($i~/cat\s{1,5}was/) print $i
        }' $filename > output.txt
    cat output.txt
done

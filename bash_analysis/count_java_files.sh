#!/bin/bash

for d in  */; do
    echo $d
    for file in `find $d -name '*.java'`; do
        echo $file;
    done | wc -l
done

cmd //c tree

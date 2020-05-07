#!/bin/bash

find . -name '*.java' | xargs wc -l | sort -nr >> loc.csv
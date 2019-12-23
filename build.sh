#!/bin/sh

python3 -B source/buildtools/builder.py linux64 debug amazons
ninja -f tmp/linux64/debug/build.ninja


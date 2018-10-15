#!/bin/bash

echo This is stdout
echo This is stderr >&2

while read input; do
	echo I received \"$input\" on stdin
done

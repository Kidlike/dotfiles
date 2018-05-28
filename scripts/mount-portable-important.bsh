#!/bin/bash

volume=~/SparkleShare/personal/portable-important.tcv

if [ -w "${volume}" ]; then
	truecrypt "${volume}"
else
	echo "External drive not connected"
	exit 1
fi

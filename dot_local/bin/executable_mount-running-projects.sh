#!/bin/bash

if [ $(mount | grep ext_ssd | wc -l) -eq 1 ]; then
	truecrypt /media/ext_ssd/projects/ericsson/running-projects.tcv
else
	echo "External drive not connected"
	exit 1
fi

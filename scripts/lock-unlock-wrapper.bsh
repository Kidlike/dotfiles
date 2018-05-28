#!/bin/bash

del=$1
shift
cmd1=$(echo $@ | sed "s/^\([^\\${del}]\+\)${del} \(.\+\)$/\1/g")
cmd2=$(echo $@ | sed "s/^\([^\\${del}]\+\)${del} \(.\+\)$/\2/g")

dbus-monitor --session "type='signal',interface='org.gnome.ScreenSaver'" | (
while true; do
	read X;
	if echo $X | grep "boolean true" &> /dev/null; then
		bash -c "$cmd1" &
	elif echo $X | grep "boolean false" &> /dev/null; then
		bash -c "$cmd2" &
	fi
done
)

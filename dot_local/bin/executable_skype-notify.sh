#!/bin/bash

if [ $# -eq 1 ]; then
	#MSG="$1"
	xdotool search --name "skype" | xargs -I {} [ ! "$(xdotool search --class skype getwindowfocus)" == "{}" ] && notify-send -i skype -t 3000 "$1"
elif [ $# -eq 2 ]; then
	#MSG="$1: $2"
	xdotool search --name "skype" | xargs -I {} [ ! "$(xdotool search --class skype getwindowfocus)" == "{}" ] && notify-send -i skype -t 3000 "$1" "$2"
else
	exit
fi

#xdotool search --name "skype" | xargs -I {} [ ! "$(xdotool search --class skype getwindowfocus)" == "{}" ] && notify-send -i skype -t 3000 "$MSG"
#xdotool search --name "skype" | xargs -I {} [ ! "$(xdotool search --class skype getwindowfocus)" == "{}" ] && notify-send -i skype -t 3000 "$1" "$2"

exit $?

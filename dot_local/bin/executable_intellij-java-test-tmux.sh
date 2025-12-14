#!/bin/bash

# $1 - ModuleFileDir - The directory of the module file
# $2 - FileDir - File directory
# $3 - FilePath - File path
# $4 - FileClass - Class name
# $5 - debug option - set to "debug" for debug mode
# $6 - LineNumber - Line number

moduleFileDir=$1
fileDir=$2
filePath=$3
fileClass=$4
lineNumber=$6

if [ "$5" == "debug" ]; then
	debug="-Dmaven.surefire.debug='-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=8002 -Xnoagent -Djava.compiler=NONE'"
else
	debug=""
fi

if [ ! -z $lineNumber ]; then
	methodName=$(head -n$lineNumber $filePath | egrep "^\s+public\s([^\s]+\s)?\w+\([^\)]*\)\s(throws\s\w)?" | tail -1 | sed -n "s#^\s\+public\s\([^\s]\+\s\)\?\(\w\+\)().*#\2#p")
	if [ -z $methodName ]; then
		echo "Could not match test's method name."
		exit 1
	fi
	whatToTest="${fileClass}#${methodName}"
else
	whatToTest="${fileClass}"
fi

tabName="$fileClass"

# open guake
xdotool keyup ctrl keyup shift keyup alt key F1
usleep 250000

# run test in separate tmux window
tmux new-window
tmux rename-window "$tabName"
sleep 1
tmux send-keys "cd $fileDir" C-m
usleep 250000
tmux send-keys "mvn-go-up" C-m
usleep 250000
tmux send-keys "mvn-dirty ${debug} clean test -Dtest=${whatToTest} -o" C-m


#!/bin/bash

file=$1

if [ $# -ne 1 ]; then
	echo "Usage: $0 <FILE>"
	exit 1
fi

touch "$file" 2>/dev/null

if [ ! -w "$file" ]; then
	echo "Cannot access '$file'"
	exit 1
fi

echo -n > "$file"

clrLn='\033[2K'
declare -a ldSymbols=("-" "\\" "|" "/")
ldI=0

for s in `gsettings list-schemas`; do
	echo -ne "${clrLn}\r$(echo ${ldSymbols[$ldI]}) $s"
	ldI=$(( ($ldI + 1) % 4 ))
	for k in `gsettings list-keys $s`; do
		echo "$s:$k=$(gsettings get $s $k)" >> "$file"
	done
done

echo -ne "${clrLn}\rDone!\n"


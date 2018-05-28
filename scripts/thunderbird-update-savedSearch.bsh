#!/bin/bash

if [ $(ps -ef | grep thunderbird | grep -v grep | grep -v $0 | wc -l) -ne 0 ]; then
    echo "Thunderbird is running. Exiting..."
    exit 1
fi

cd "$(find /home/kalantziss/.thunderbird/ -maxdepth 1 -type d | head -2 | tail -1)"
lineFromStart=$(grep -n 'uri=imap://kalantziss@dub-cas.iconcr.com/_work' virtualFolders.dat | cut -d\: -f1)
lineFromEnd=$(($(wc -l virtualFolders.dat | cut -d\  -f1) - ${lineFromStart} + 1));

changedTerms=$(tail -${lineFromEnd} virtualFolders.dat | egrep '^terms=' | head -1 | sed "s/(date,is after,[0-9]\{2\}-[a-zA-Z]\{3\}-[0-9]\{4\})/(date,is after,$(date -d "-40 days" +%d-%b-%Y))/g")

sed -i "$(($lineFromStart+2))s/^.*$/${changedTerms}/" virtualFolders.dat


#!/bin/bash

find target/surefire-reports/*.txt | while read -r f; do
    noFailures=$(grep -c 'Failures: 0' $f)
    noErrors=$(grep -c 'Errors: 0' $f)
    if [ $noFailures -eq 0 -o $noErrors -eq 0 ]; then
        echo "- [] "$(grep 'Test set' $f | cut -d\: -f2)
    fi
done

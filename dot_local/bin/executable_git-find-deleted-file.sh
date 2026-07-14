#!/bin/bash

set -eu

filename=${1:?Please provide filename}

firstCommit=$(git rev-list --max-parents=0 HEAD)

git bisect start
git bisect bad
git bisect good "${firstCommit}"

previous=""
next="next"
while [[ "$previous" != "$next" ]]; do
    previous="$next"
    if [[ $(find . -type f -name "${filename}" | wc -l) -eq 0 ]]; then
        next=$(git bisect bad | tee /dev/stderr)
    else
        next=$(git bisect good | tee /dev/stderr)
    fi
done

echo
echo "======================================================================"

git bisect reset


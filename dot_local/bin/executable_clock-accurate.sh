#!/bin/bash

function _time() {
  date +"%H:%M:%S.%3N" | grep -E --color=always -e '^' -e ':00\.0[0-9]+'
}

while true; do
  _time
  left=$(echo "scale=10; 1 - ( $(date +%N) / 1000000000 )" | bc)
  sleep 0$left
done

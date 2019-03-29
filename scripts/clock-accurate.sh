#!/bin/bash

function _time() {
  date +"%H:%M:%S.%3N"
}

while true; do
  _time
  left=$(echo "scale=10; 1 - ( $(date +%N) / 1000000000 )" | bc)
  sleep 0$left
done

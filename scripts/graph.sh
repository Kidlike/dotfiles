#!/bin/env bash

LOG=$1
IMAGE=$(mktemp)

gnuplot <<EOL
set title "${2:-$1}"
set term png small size 1920,1080
set output "$IMAGE"
set ylabel "RSS"
set y2label "VSZ"
set ytics nomirror
set y2tics nomirror in
set yrange [0:*]
set y2range [0:*]
plot "$LOG" using 3 with lines axes x1y1 title "RSS", "$LOG" using 2 with lines axes x1y2 title "VSZ"
EOL

xdg-open $IMAGE


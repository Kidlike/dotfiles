#!/bin/bash

sudo echo

mvn $@ 2>&1 &
pid=$!

sudo iotop --pid=$pid --batch --time > performance.log

#sudo iotop --pid=$pid --batch --kilobytes --time --iter=1 -qqq > performance.log
#while [ "$(kill -0 $pid 2> /dev/null && echo true || echo false)" == "true" ]; do
#	sudo iotop --pid=$pid --batch --kilobytes --time --iter=1 -qqq >> performance.log
#done

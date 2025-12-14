#!/bin/bash

[ `whoami` = root ] || exec sudo su -c $0

killall dnsmasq
ap-hotspot start
service network-manager restart

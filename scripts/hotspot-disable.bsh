#!/bin/bash

[ `whoami` = root ] || exec sudo su -c $0

ap-hotspot stop
killall dnsmasq
service network-manager restart

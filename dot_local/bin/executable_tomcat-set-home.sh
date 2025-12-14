#!/bin/bash

if [ -z $1 ]; then
    exit
fi

cd /opt
rm -f tomcat
ln -sf $1 tomcat


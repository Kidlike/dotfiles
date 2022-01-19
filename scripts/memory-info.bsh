#!/bin/bash

oldIFS=$IFS
IFS=\

var_stats=`vmstat -s | tr -s ' ' ' ' | cut -d\  -f 2`;

#echo $var_stats

var_total_memory=`echo $var_stats | head -1`
var_free_memory1=`echo $var_stats | head -4 | tail -1`
var_free_memory2=`echo $var_stats | head -5 | tail -1`
var_free_memory=`expr $var_free_memory1 + $var_free_memory2`
var_used_swap=`echo $var_stats | head -9 | tail -1`
var_used_memory=`expr $var_total_memory - $var_free_memory`

echo "used memory : $var_used_memory"
echo "free memory : $var_free_memory"
echo "used swap   : $var_used_swap"

IFS=$oldIFS

#exit 0

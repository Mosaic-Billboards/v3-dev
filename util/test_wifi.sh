#!/bin/bash
# test_wifi_connection -> Ping 2 servers and exit w/ result

ping_address1="1.1.1.1"
ping_address2="8.8.8.8"
ping_cmd1=$(echo ping -c 2 -W 5 $ping_address1)
ping_cmd1=$(echo ping -c 2 -W 5 $ping_address2)

$ping_cmd1
ping_result1=$?
$ping_cmd2
ping_result2=$?

if [[ $ping_result1 == 0 ]] || [[ $ping_result2 == 0 ]]; then
    exit 0
else
    exit 1
fi
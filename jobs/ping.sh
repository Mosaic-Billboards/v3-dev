#!/bin/bash
# ping.sh --> ping database that billboard is online

sh ../util/test_wifi.sh
wifi_status=$?

if [[ $wifi_status == 0 ]]; then
    token=$TOKEN
    curl -H "Authorization: Bearer $token" $ping_endpoint
    exit 0
else
    exit 1
fi
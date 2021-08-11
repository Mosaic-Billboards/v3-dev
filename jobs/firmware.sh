#!/bin/bash
# firmware.sh --> check firmware

sh ../util/test_wifi.sh
wifi_status=$?

if [[ $wifi_status == 0 ]]; then
    /usr/bin/env python3 /usr/bin/hagrid/jobs/firmware.py
    exit 0
else
    exit 1
fi
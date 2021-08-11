#!/bin/bash
# fetch_handle_ads.sh --> get ads, download content, delete ads, write to schedule

sh ../util/test_wifi.sh
wifi_status=$?

if [[ $wifi_status == 0 ]]; then
    /usr/bin/env python3 /usr/bin/hagrid/jobs/ads/fetch_ads.py
    exit 0
else
    exit 1
fi
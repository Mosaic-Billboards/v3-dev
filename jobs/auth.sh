#!/bin/bash
# auth.sh --> sign in with Firebase Auth

sh ../util/test_wifi.sh
wifi_status=$?

if [[ $wifi_status == 0 ]]; then
    /usr/bin/env python3 /usr/bin/hagrid/jobs/auth.py
    exit 0
else
    exit 1
fi
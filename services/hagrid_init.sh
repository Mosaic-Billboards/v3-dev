#!/bin/bash
# hagrid_init --> Determine if system enters setup_mode (BLE pairing) or live_mode (displaying advertisements)

billboard_id=$BILLBOARD_ID
if [[ $(whoami) != $billboard_id ]]; then
    exit 1
fi

db_path="/usr/bin/hagrid/data.sqlite"
wpa_supplicant_path="/etc/wpa_supplicant/wpa_supplicant.conf"

db_has_future_cmd=$(/usr/bin/env python3 /usr/bin/hagrid/services/db_has_future.py)

start_setup_mode() {
    setup_mode_enter_path="/usr/bin/hagrid/setup_mode/setup_mode.py"
    bluetoothctl power on
    bluetoothctl set-alias $billboard_id
    /usr/bin/env python3 $setup_mode_enter_path
}

start_live_mode() {
    live_mode_enter_path="/usr/bin/hagrid/live_mode/live_mode.py"
    bluetoothctl power off
    /usr/bin/env python3 $live_mode_enter_path
}

# if wpa_supplicant doesn't exist
# then start setup_mode
-s $wpa_supplicant_path
if [[ $? != 0 ]]; then
    start_setup_mode
fi

# if db exists, and db has future items
# then start_live_mode else setup_mode
-s $db_path
if [[ $? == 0 ]]; then
    $db_has_future_cmd
    if [[ $? == 0 ]]; then
        start_live_mode
    else 
        start_setup_mode
    fi
else
    start_setup_mode
fi


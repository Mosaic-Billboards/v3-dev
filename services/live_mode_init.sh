#!/bin/bash
# live_mode_init.sh --> Initialization for live_mode after network-online.target

# Kill any BLE devices and power down
ble_release_path="../utilities/ble_release.sh"
sh $ble_release_path
bluetoothctl power down

setup_mode_pid=$(ps aux | grep '[p]ython3 setup_mode.py' | awk '{print $2}')
live_mode_pid=$(ps aux | grep '[p]ython3 live_mode.py' | awk '{print $2}')

# Kill any setup_mode.py processes
$setup_mode_pid
if [ $? == 0 ]; then
    kill $setup_mode_pid
fi

# Determines if hagrid-online.service should execute live_mode
$live_mode_pid
if [ $? == 0 ]; then
    exit 1
else
    exit 0
fi
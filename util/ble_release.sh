#!/bin/bash
# ble_release -> Disconnect from devices and cycle power

for (( ; ; ))
do
    bluetoothctl info
    has_devices=$?
    if [[ $has_devices == 0 ]]; then
        device_id=$(bluetoothctl info | awk 'FNR == 1 {print $2}')
        bluetoothctl remove $device_id
    else
        break
    fi
done

exit 0
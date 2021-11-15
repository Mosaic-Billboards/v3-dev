# v3-firmware-dev

Custom linux firmware system for IoT digital billboards.

Boots into different modes depending on WiFi connection status:
(boot controlled by systemd services in /services)
- setup_mode
- live_mode

## setup_mode
- Interacts with bluetooth stack (BlueZ) through DBus
- BLE advertising, awaits connection, handles process for validating connection, recieves WiFi creds, and connects.

- ble_objects.py --> Base BLE classes for Application, Service, Characteristic, and Descriptor
- ble_app.py --> Custom service, 4 control characteristics, and state classes.

## live_mode
- handles content rotation loop
- interacts with display controller and local SQLite data

## jobs
A variety of cron jobs
1. ping -> pings backend once a minute.
2. auth -> refreshes billboard auth token once every 50 min.
3. firmware -> checks firmware updates once an hour.
4. fetch_handle_owner_ads -> fetches and inserts billboard owner created content every 5 minutes.
5. fetch_handle_ads -> fetches and handles new paid ads/expired ads every 4 hours.

# display
- simple Python Tkinter process
- we create a pipe that can recieve messages from other processes

# about this code
This system isn't fully functional, parts work, other parts don't, but there's code others may find useful, so thought to make it public.

Built by Aaren Stade, Summer 2021

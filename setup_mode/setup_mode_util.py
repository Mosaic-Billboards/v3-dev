import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import dbus
import time

import subprocess as sp
from wifi import Cell, Scheme

from ble_constants import (
    BLUEZ_SERVICE_NAME,
    DBUS_OM_IFACE,
    GATT_MANAGER_IFACE,
    WPA_SUPPLICANT_PATH,
)

from log import define_logger
logger = define_logger('SETUP_MODE', __name__)

from util.general import retrieve_user_password, retrieve_billboard_secret

'''
---------------------------------------------
D-Bus Helpers
---------------------------------------------
'''

def find_adapter(bus):
    # Returns the first object that the bluez service has that has a GattManager1 interface
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None

def decode_dbus_value(data):
    newVal = ''.join([str(v) for v in data])
    return newVal


def encode_dbus_value(data):
    return bytearray(str(data), 'utf-8')

'''
---------------------------------------------
WiFi/BLE Helpers
---------------------------------------------
'''

# return max 5 result
def scan_wifi_routers():
    print('scanning wifi routers')
    routers = []
    cell = Cell.all('wlan0')
    for r in cell:
        if len(r.ssid) > 0:
            if not '\x00' in r.ssid:
                routers.append(r.ssid)
    if len(routers) > 5:
        return routers[0:4]
    print(f'got routers: {routers}')
    return routers

def test_wifi():
    wifi_test = sp.Popen('sh scripts/test_wifi.sh', stdout=sp.PIPE)
    wifi_test.communicate()[0]
    return wifi_test.returncode

def connect_and_test_wifi(ssid, password, security):
    print('connecting and testing wifi')
    with open(WPA_SUPPLICANT_PATH, "w") as wpa_file:
        wpa_data = """
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=%s
        network={
            ssid="%s"
            psk="%s"
            key_mgmt=WPA-PSK
        }
        """ % ('US', ssid, password)
        print(f'WPA DATA: {wpa_data}')
        # TODO: add country code characteristic
        wpa_file.write(wpa_data)
    logger.info('wpa_supplicant.conf written')
    user_password = bytearray(retrieve_user_password(), 'utf-8')
    sp.run('systemctl restart wpa_supplicant.service', input=user_password)
    sp.run('systemctl restart dhcpcd.service', input=user_password)
    logger.info('systemd network services restarted')
    time.sleep(5)
    exit_code = test_wifi()
    print(f'got exit_code: {exit_code}')
    if exit_code == 0:
        return True
    else:
        return False
    

def release_ble():
    print('releasing ble')
    sp.run('sh scripts/ble_release.sh')
    sp.run('bluetoothctl power off')
    sp.run('bluetoothctl power on')
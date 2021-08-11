'''
---------------------------------------------
D-Bus and BlueZ
---------------------------------------------
'''

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE = "org.bluez.GattDescriptor1"
DEVICE_IFACE = "org.bluez.Device1"

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
AGENT_IFACE = "org.bluez.Agent1"
AGENT_PATH = "/com/mosaicbillboards/agent"

char_uuids = [
    #config uuids
    "f076d880-f1cf-4a63-a98c-15ac2b7a7538",
    "cd7c924f-d0b5-490f-b75d-8be8ccc9fb76",
    "0f0ed0d6-bccf-468f-81e2-b8b285d9a662",
    "859b5a42-b498-4218-8004-63ca947ba4d3",   
    # scan uuids
    "1c5dec7a-bc4d-450b-881f-8c85af627d00",
    "5698cd0b-6f3c-4d44-8ac6-7ca002e80b7c",
    "8debe234-7d9f-4bae-900b-d726a7d88e1b",
    "c53ffb0d-2149-46de-9848-a5abc174a81a",
    "360f49c8-9627-4154-9692-c5f153a91fd6",
    "4871595b-9807-418b-95af-307be60690e1"  
]

char_names = [
    'WIFI_STATE',
    'WIFI_SSID',
    "WIFI_PASSWORD",
    "WIFI_SECURITY",
    
    "WIFI_SCAN_REFRESH",
    "WIFI_SCAN_1",
    "WIFI_SCAN_2",
    "WIFI_SCAN_3",
    "WIFI_SCAN_4",
    "WIFI_SCAN_5",
]

'''
---------------------------------------------
PATHS
---------------------------------------------
'''

WPA_SUPPLICANT_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"


# EXCEPTIONS
import dbus.exceptions

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


class RejectedException(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

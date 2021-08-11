#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import dbus
import dbus.mainloop.glib
import dbus.service

import logging
import array
import time
import random

MainLoop = None
try:
    from gi.repository import GLib
    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject
    MainLoop = GObject.MainLoop


from ble_objects import (
    Characteristic,
    Service,
    Advertisement,
    Application,
    Descriptor,
    Agent,
)

from setup_mode_util import (
    find_adapter,
    decode_dbus_value,
    encode_dbus_value,
    retrieve_billboard_secret,
    scan_wifi_routers,
    connect_and_test_wifi,
    release_ble,
    file_read,
    file_write
)

from dotenv import load_dotenv
load_dotenv()
BILLBOARD_ID = os.environ.get('BILLBOARD_ID')

from ble_constants import (
    BILLBOARD_ID,
    BLUEZ_SERVICE_NAME, 
    LE_ADVERTISING_MANAGER_IFACE,
    GATT_MANAGER_IFACE,
    AGENT_PATH,
    char_uuids,
    char_names,
)

from log import define_logger
logger = define_logger('SETUP_MODE', __name__)

mainloop = None

# -------- DEBUG LOGGING --------

def register_app_cb():
    logger.info("GATT application registered")


def register_app_error_cb(error):
    logger.critical("Failed to register application: " + str(error))
    mainloop.quit()


def register_ad_cb():
    logger.info("Advertisement registered")


def register_ad_error_cb(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()

WIFI_STATE_IDLE = 0
WIFI_STATE_AUTH = 1
WIFI_STATE_AUTH_SUCCESS = 2
WIFI_STATE_AUTH_FAIL = 3
WIFI_STATE_SCAN = 4
WIFI_STATE_JOIN = 5
WIFI_STATE_JOINING = 6
WIFI_STATE_JOIN_SUCCESS = 7
WIFI_STATE_JOIN_FAIL = 8

state = None  
      
class Global_State:
    def __init__(self):
        self.authenticated = False
        self.wifi_ssid = ""
        self.wifi_password = ""
        self.wifi_security = ""
        self.wifi_scan_ssids = []
    def set_wifi_scan_results(self, results):
        self.wifi_scan_ssids = results

class Hagrid_Application(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)

class Hagrid_Advertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_local_name(BILLBOARD_ID)
        self.add_service_uuid(Hagrid_Primary_Service.SERV_ID)

class Description_Descriptor(Descriptor):
    CUD_UUID = str(random.randint(0, 9999))
    def __init__(self, bus, index, characteristic):
        self.value = array.array("B", characteristic.description).tolist()
        Descriptor.__init__(self, bus, index, self.CUD_UUID, ['read'], characteristic)
    def ReadValue(self, options):
        return self.value
    def WriteValue(self, value, options):
        self.value = value

class WiFi_State_Char(Characteristic):
    def __init__(self, bus, index, service):
        CHAR_ID = char_uuids[index]
        Characteristic.__init__(self, bus, index, CHAR_ID, ['encrypt-read', 'encrypt-write'], service)
        self.value = [0x00]
        self.description = bytes(str(char_names[index]), 'utf-8')       
        self.add_descriptor(Description_Descriptor(bus, 1, self))
    def ReadValue(self, options):
        return encode_dbus_value(self.value)
    def WriteValue(self, value, options={"type":"command"}):
        global state
        command = int(decode_dbus_value(value))
        logger.info(f'WiFi_State_Char write: {command}')
        if command == WIFI_STATE_AUTH:
            print('entered WIFI_STATE_AUTH')
            secret = state.wifi_password    
            saved_secret = retrieve_billboard_secret()
            print(f"saved_secret={saved_secret} compare with secret={secret}")
            if secret == saved_secret:
                state.authenticated = True
                print('setting WIFI_STATE_AUTH_SUCCESS')
                self.value = WIFI_STATE_AUTH_SUCCESS
            else:   
                print('setting WIFI_STATE_AUTH_FAIL')
                state.authenticated = False
                self.value = WIFI_STATE_AUTH_FAIL
                time.sleep(1)
                release_ble()
        if command == WIFI_STATE_JOIN and state.authenticated == True:
            print('entered WIFI_STATE_JOIN && authenticated == True')
            ssid = state.wifi_ssid
            password = state.wifi_password
            security = state.wifi_security
            print(f'got values ssid: {ssid}, password: {password}, security: {security}')
            result = connect_and_test_wifi(ssid, password, security)
            if result == True:
                print('setting WIFI_STATE_JOIN_SUCCESS')
                self.value = WIFI_STATE_JOIN_SUCCESS
            else:
                print('setting WIFI_STATE_JOIN_FAIL')
                self.value = WIFI_STATE_JOIN_FAIL
                time.sleep(3)
                print('setting WIFI_STATE_SCAN')
                self.value = WIFI_STATE_SCAN         

class WiFi_Config_Char(Characteristic):
    def __init__(self, bus, index, service):
        CHAR_ID = char_uuids[index]
        Characteristic.__init__(self, bus, index, CHAR_ID, ['encrypt-write'], service)
        self.name = char_names[index]
        self.description = bytes(str(self.name), 'utf-8')       
        self.add_descriptor(Description_Descriptor(bus, 1, self))
        self.value = ""
    def WriteValue(self, value, options={"type":"command"}):
        global state
        val = decode_dbus_value(value)
        if self.name == "WIFI_SSID":
            logger.info(f'WiFi_Config_Char SSID write: {val}')
            state.wifi_ssid = val
        if self.name == "WIFI_PASSWORD":
            logger.info(f'WiFi_Config_Char PASSWORD write: {val}')
            state.wifi_password = val
        if self.name == "WIFI_SECURITY":
            logger.info(f'WiFi_Config_Char SECURITY write: {val}')
            state.wifi_security = val
        self.value = value
    
class WiFi_Scan_Refresh_Char(Characteristic):
    def __init__(self, bus, index, service):
        CHAR_ID = char_uuids[index]
        Characteristic.__init__(self, bus, index, CHAR_ID, ['read'], service)
        self.description = bytes("WIFI_SCAN_REFRESH", 'utf-8')       
        self.add_descriptor(Description_Descriptor(bus, 1, self))
        self.value = 0
    def ReadValue(self, options):
        global state
        scan_results = scan_wifi_routers()
        state.set_wifi_scan_results(scan_results)
        self.value = encode_dbus_value(len(scan_results))
        logger.info(f'WiFi scan refresh char read: {self.value}')
        return self.value
        
class WiFi_Scan_Char(Characteristic):
    def __init__(self, bus, index, service):
        CHAR_ID = char_uuids[index]
        Characteristic.__init__(self, bus, index, CHAR_ID, ['read'], service)
        self.description = bytes(str(char_names[index]), 'utf-8')     
        self.value = ""  
        self.add_descriptor(Description_Descriptor(bus, 1, self))
        self.id = index
    def ReadValue(self, options):
        try:
            global state
            name = char_names[self.id] 
            char_index = int(name[10:])
            if (len(state.wifi_scan_ssids) >= char_index):
                ssid = state.wifi_scan_ssids[char_index - 1] 
                self.value = encode_dbus_value(ssid)
                logger.info(f'WiFi_Scan_Char {name} read value: {self.value}')
                return self.value
        except:
            error = sys.exc_info()[0]
            logger.error(f'WiFi_Scan_Char {char_names[self.id]} read value except: {error}')
            return self.value
    
class Hagrid_Primary_Service(Service):
    SERV_ID = "a2f3e213-6408-463a-abd2-7af0431b20df"
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SERV_ID, True)
        self.add_characteristic(WiFi_State_Char(bus, 0, self))
        self.add_characteristic(WiFi_Config_Char(bus, 1, self))
        self.add_characteristic(WiFi_Config_Char(bus, 2, self))
        self.add_characteristic(WiFi_Config_Char(bus, 3, self))
        
        self.add_characteristic(WiFi_Scan_Refresh_Char(bus, 4, self))
        self.add_characteristic(WiFi_Scan_Char(bus, 5, self))
        self.add_characteristic(WiFi_Scan_Char(bus, 6, self))
        self.add_characteristic(WiFi_Scan_Char(bus, 7, self))
        self.add_characteristic(WiFi_Scan_Char(bus, 8, self))
        self.add_characteristic(WiFi_Scan_Char(bus, 9, self))
    
def start_advertising(ble_object):
    global mainloop
    
    bluez_ref = ble_object.bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    # Get manager objs
    gatt_manager = dbus.Interface(ble_object.adapter, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(ble_object.adapter, LE_ADVERTISING_MANAGER_IFACE)
    agent_manager = dbus.Interface(bluez_ref, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    agent = Agent(ble_object.bus, AGENT_PATH)

    ad_manager.RegisterAdvertisement(
        ble_object.advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    logger.info("Registering GATT application...")
    gatt_manager.RegisterApplication(
        ble_object.application.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=register_app_error_cb,
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)
    
    global state
    state = Global_State()

    mainloop = MainLoop()
    mainloop.run()
    
    
def stop_advertising(ble_object):
    ad_manager = dbus.Interface(ble_object.adapter, LE_ADVERTISING_MANAGER_IFACE)
    ad_manager.UnregisterAdvertisement(ble_object.advertisement)
    dbus.service.Object.remove_from_connection(ble_object.advertisement)
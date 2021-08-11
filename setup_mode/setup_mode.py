#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '/')))

import dbus 

import subprocess as sp

from ble_app import (
    Hagrid_Application,
    Hagrid_Advertisement,
    Hagrid_Primary_Service,
    start_advertising
)

from dotenv import load_dotenv
load_dotenv()
BILLBOARD_ID = os.environ.get('BILLBOARD_ID')

from ble_constants import BLUEZ_SERVICE_NAME

from setup_mode_util import find_adapter, exit

from log import define_logger
logger = define_logger('SETUP_MODE', __name__)



class HagridBLE:
    def __init__(self):
        self.bus = None
        self.adapter = None
        self.application = None
        self.advertisement = None
        self.services = []

    def set_bus(self, bus):
        self.bus = bus

    def set_adapter(self, adapter):
        self.adapter = adapter

    def set_application(self, application):
        self.application = application

    def set_advertisement(self, advertisement):
        self.advertisement = advertisement

def main():
    ble_object = HagridBLE()
    
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    if not adapter:
        logger.critical("GattManager1 interface not found")
        exit(1)
    
    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)
    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))
    
    advertisement = Hagrid_Advertisement(bus, 0)
    app = Hagrid_Application(bus)
    
    app.add_service(Hagrid_Primary_Service(bus, 0))
    
    ble_object.set_bus(bus)
    ble_object.set_adapter(adapter_obj)
    ble_object.set_application(app)
    ble_object.set_advertisement(advertisement)
    
    start_advertising(ble_object)
    

if __name__ == "__main__":
    main()
    



#! /usr/bin/python3

from sump.mqtt.constants import Constants
from sump.mqtt.mqtt_sump_buttons import MQTTSumpButtons
from sump.mqtt.mqtt_sump_tank_watcher import MQTTSumpTankWatcher
from sump.mqtt.mqtt_sump_db_write import MQTTSumpDBWrite
from sump.mqtt.mqtt_sump_relay import MQTTSumpRelay
from sump.mqtt.mqtt_sump_rpi import MQTTSumpRPi
from sump.mqtt.mqtt_sump_status import MQTTSumpStatus
from sump.mqtt.mqtt_sump_processor import MQTTSumpProcessor
from sump.mqtt.mqtt_publisher_base import MQTTPublisherBase

import argparse
import traceback

from sump.utilities.status import DeviceStatus, LEDnames

class SumpStarter(MQTTPublisherBase):
    def __init__(self) -> None:
        super().__init__(Constants.MQTT_HOST, Constants.MQTT_PORT, "SumpStarter", "Sump/Command/App/", 2)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Manage dirty water pump")
        group = parser.add_mutually_exclusive_group(required = True)
        group.add_argument("-m", "--measure", action="store_true", help="Measure the distance")
        group.add_argument("-b", "--buttons", action="store_true", help="Launch button MQTT")
        group.add_argument("-d", "--database", action="store_true", help="Launch DB MQTT")
        group.add_argument("-p", "--processor", action="store_true", help="Launch processor MQTT")
        group.add_argument("-R", "--Rpi", action="store_true", help="Launch RPi MQTT")
        group.add_argument("-r", "--relay", action="store_true", help="Launch relay MQTT")
        group.add_argument("-s", "--status", action="store_true", help="Launch status MQTT")
        group.add_argument("-t", "--tank_watcher", action="store_true", help="Launch tank watcher MQTT")
        
        args = parser.parse_args()
        
        if args.measure:
            SumpStarter().post_message(f"{LEDnames.SENSOR_AUTO}", f"{DeviceStatus.WORKING.name}", False)
        elif args.buttons:
            MQTTSumpButtons().start()
        elif args.database:
            MQTTSumpDBWrite().start()
        elif args.processor:
            MQTTSumpProcessor().start()
        elif args.Rpi:
            MQTTSumpRPi().start()
        elif args.relay:
            MQTTSumpRelay().start()
        elif args.status:
            MQTTSumpStatus().start()
        elif args.tank_watcher:
            MQTTSumpTankWatcher().start()
        else:
            parser.print_help()
    except Exception as e:
        traceback.print_exc()
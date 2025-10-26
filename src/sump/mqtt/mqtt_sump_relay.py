#! /usr/bin/python3

from core.relay_module import RelayDecoder
from mqtt.constants import Constants
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.status import GeneralStatus

import json
import RPi.GPIO as gpio

class MQTTSumpRelay(MQTTSubscriberBase):
    def __init__(self) -> None:
        super().__init__(Constants.MQTT_HOST, Constants.MQTT_PORT, "RelaySubscriber", "Sump/Relay", 2)
    
    def on_message_callback(self, client, userdata, message):
        received_data = json.loads(message.payload.decode(), cls=RelayDecoder)
        
        received_data.switch_to_general_status()
        
        if received_data.general_status == GeneralStatus.OFF:
            gpio.cleanup()

if __name__ == '__main__':
    MQTTSumpRelay().start()
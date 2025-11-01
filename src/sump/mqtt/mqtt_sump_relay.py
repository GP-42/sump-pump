#! /usr/bin/python3

from core.relay_module import RelayDecoder
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.configuration.toml.toml_configuration import TomlConfiguration
from utilities.status import GeneralStatus

import json
import RPi.GPIO as gpio

class MQTTSumpRelay(MQTTSubscriberBase):
    def __init__(self) -> None:
        self.config = TomlConfiguration()
        super().__init__(self.config.MQTTSumpRelay.host, self.config.MQTTSumpRelay.port, self.config.MQTTSumpRelay.client_id, self.config.MQTTSumpRelay.subscription_topic, self.config.MQTTSumpRelay.message_qos)
    
    def on_message_callback(self, client, userdata, message):
        received_data = json.loads(message.payload.decode(), cls=RelayDecoder)
        
        received_data.switch_to_general_status()
        
        if received_data.general_status == GeneralStatus.OFF:
            gpio.cleanup()

if __name__ == '__main__':
    MQTTSumpRelay().start()
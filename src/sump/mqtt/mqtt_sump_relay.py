#! /usr/bin/python3

from sump.core.relay_module import RelayDecoder
from sump.mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from sump.utilities.configuration.classic.env_configuration import EnvConfiguration
from sump.utilities.configuration.toml.toml_configuration import TomlConfiguration
from sump.utilities.status import GeneralStatus

import json
import RPi.GPIO as gpio

class MQTTSumpRelay(MQTTSubscriberBase):
    def __init__(self) -> None:
        self.TomlConfig = TomlConfiguration()
        self.EnvConfig = EnvConfiguration()
        super().__init__(self.TomlConfig.MQTTSumpRelay.host, self.TomlConfig.MQTTSumpRelay.port, self.EnvConfig.SumpRelayCredentials.MQTTUser, \
                         self.EnvConfig.SumpRelayCredentials.MQTTPassword, self.TomlConfig.MQTTSumpRelay.client_id, \
                         self.TomlConfig.MQTTSumpRelay.subscription_topic, self.TomlConfig.MQTTSumpRelay.message_qos)
    
    def on_message_callback(self, client, userdata, message):
        received_data = json.loads(message.payload.decode(), cls=RelayDecoder)
        
        received_data.switch_to_general_status()
        
        if received_data.general_status == GeneralStatus.OFF:
            gpio.cleanup()

if __name__ == '__main__':
    MQTTSumpRelay().start()
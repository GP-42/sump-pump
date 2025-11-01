#! /usr/bin/python3

from core.measurement import Measurement, MeasurementDecoder
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.configuration.classic.env_configuration import EnvConfiguration
from utilities.configuration.toml.toml_configuration import TomlConfiguration
from utilities.status import SystemStatusItem, SystemStatusItemDecoder

import json

class MQTTSumpDBWrite(MQTTSubscriberBase):
    def __init__(self) -> None:
        self.TomlConfig = TomlConfiguration()
        self.EnvConfig = EnvConfiguration()
        super().__init__(self.TomlConfig.MQTTSumpDBWrite.host, self.TomlConfig.MQTTSumpDBWrite.port, self.EnvConfig.SumpDBWriteCredentials.MQTTUser, \
                         self.EnvConfig.SumpDBWriteCredentials.MQTTPassword, self.TomlConfig.MQTTSumpDBWrite.client_id, \
                         self.TomlConfig.MQTTSumpDBWrite.subscription_topic, self.TomlConfig.MQTTSumpDBWrite.message_qos)
    
    def on_message_callback(self, client, userdata, message):
        current_topic = self.get_last_subtopic(message.topic)
        if current_topic == Measurement().__class__.__name__:
            received_data = json.loads(message.payload.decode(), cls=MeasurementDecoder)
            received_data.save_to_db()
        elif current_topic == SystemStatusItem().__class__.__name__:
            received_data = json.loads(message.payload.decode(), cls=SystemStatusItemDecoder)
            received_data.save_to_db()

if __name__ == '__main__':
    MQTTSumpDBWrite().start()
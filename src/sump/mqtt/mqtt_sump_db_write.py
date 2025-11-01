#! /usr/bin/python3

from core.measurement import Measurement, MeasurementDecoder
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.configuration.toml.toml_configuration import TomlConfiguration
from utilities.status import SystemStatusItem, SystemStatusItemDecoder

import json

class MQTTSumpDBWrite(MQTTSubscriberBase):
    def __init__(self) -> None:
        self.config = TomlConfiguration()
        super().__init__(self.config.MQTTSumpDBWrite.host, self.config.MQTTSumpDBWrite.port, self.config.MQTTSumpDBWrite.client_id, self.config.MQTTSumpDBWrite.subscription_topic, self.config.MQTTSumpDBWrite.message_qos)
    
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
#! /usr/bin/python3

from sump.core.measurement import MeasurementEncoder
from sump.core.tank_watcher import TankWatcher
from sump.mqtt.exceptions import InvalidTopicError
from sump.mqtt.mqtt_publisher_base import MQTTPublisherBase
from sump.mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from sump.utilities.configuration.classic.env_configuration import EnvConfiguration
from sump.utilities.configuration.toml.toml_configuration import TomlConfiguration
from sump.utilities.status import DeviceStatus, LEDnames

import json

class MQTTSumpTankWatcher(MQTTPublisherBase, MQTTSubscriberBase):
    def __init__(self) -> None:
        self.TomlConfig = TomlConfiguration()
        self.EnvConfig = EnvConfiguration()
        super().__init__(self.TomlConfig.MQTTSumpTankWatcher.host, self.TomlConfig.MQTTSumpTankWatcher.port, self.EnvConfig.SumpTankWatcherCredentials.MQTTUser, \
                         self.EnvConfig.SumpTankWatcherCredentials.MQTTPassword, self.TomlConfig.MQTTSumpTankWatcher.client_id, \
                         self.TomlConfig.MQTTSumpTankWatcher.publisher_root_topic, self.TomlConfig.MQTTSumpTankWatcher.message_qos)
        self.subscription_topic = self.TomlConfig.MQTTSumpTankWatcher.subscription_topic
        self.allowed_topics = [LEDnames.SENSOR_AUTO, LEDnames.SENSOR_MANUAL]
    
    def on_message_callback(self, client, userdata, message):
        topic = self.get_last_subtopic(message.topic)
        if topic in self.allowed_topics:
            status_value = str(message.payload.decode("utf-8"))
            is_automatic = status_value.endswith("_AUTO")
            
            # Not necessary because always called from processor
            # self.post_message_activity_status(is_automatic, True)            
            result = TankWatcher.measure(is_automatic)
            converted = json.dumps(result, cls=MeasurementEncoder)
            self.post_message("DB/Measurement", converted, False)
            self.post_message_activity_status(is_automatic, False)
            self.post_message("Command/App/Measurement", f"{result.water_depth}", False)
        else:
            raise InvalidTopicError(message.topic)

    def post_message_activity_status(self, automatic, start):
        led_name = LEDnames.SENSOR_AUTO if automatic else LEDnames.SENSOR_MANUAL
        message = DeviceStatus.WORKING.name if start else DeviceStatus.STOP_WORKING.name
        self.post_message(f"Command/App/{led_name}", f"{message}", False)

if __name__ == '__main__':
    MQTTSumpTankWatcher().start()
#! /usr/bin/python3

from core.measurement import MeasurementEncoder
from core.tank_watcher import TankWatcher
from mqtt.constants import Constants
from mqtt.exceptions import InvalidTopicError
from mqtt.mqtt_publisher_base import MQTTPublisherBase
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.status import DeviceStatus, LEDnames

import json

class MQTTSumpTankWatcher(MQTTPublisherBase, MQTTSubscriberBase):
    def __init__(self) -> None:
        super().__init__(Constants.MQTT_HOST, Constants.MQTT_PORT, "TankWatcher", "Sump/", 2)
        self.subscription_topic = "Sump/Sensor/+"
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
#! /usr/bin/python3

from abc import ABCMeta
from sump.mqtt.mqtt_manager import MQTTManager

import traceback

class MQTTPublisherBase(metaclass=ABCMeta):
    def __init__(self, mqtt_host, mqtt_port, mqtt_user, mqtt_password, client_id, publisher_root_topic, message_qos) -> None:
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.client_id = client_id
        self.publisher_root_topic = publisher_root_topic
        self.message_qos = message_qos
    
    def post_message(self, topic, message, retain_message):
        try:
            publisher = MQTTManager(self.mqtt_host, self.mqtt_port, self.mqtt_user, self.mqtt_password, self.client_id, False)
            publisher.publish(f"{self.publisher_root_topic}{topic}", message, retain_message)
        except Exception:
            print(traceback.format_exc())
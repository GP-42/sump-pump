#! /usr/bin/python3

from abc import ABCMeta, abstractmethod
from mqtt.mqtt_manager import MQTTManager

import time
import traceback

class MQTTSubscriberBase(metaclass=ABCMeta):
    def __init__(self, mqtt_host, mqtt_port, client_id, subscription_topic, message_qos) -> None:
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.client_id = client_id
        self.subscription_topic = subscription_topic
        self.message_qos = message_qos
        self.processing_message = False

    def on_connect(self, client, userdata, connect_flags, reason_code, properties):
        client.subscribe(self.subscription_topic, self.message_qos)

    def on_message(self, client, userdata, message):
        try:
            self.safe_to_proceed()
            
            self.processing_message = True
            
            self.on_message_callback(client, userdata, message)

            self.processing_message = False
        except Exception:
            print(traceback.format_exc())
    
    @abstractmethod
    def on_message_callback(self, client, userdata, message):
        pass

    def safe_to_proceed(self):
        while self.processing_message:
            time.sleep(0.2)

    @staticmethod
    def get_last_subtopic(topic):
        return topic[topic.rfind("/") + 1:]

    @staticmethod
    def split_topic(topic):
        return topic.split("/")
    
    def start_initializer(self):
        pass

    def start(self):
        try:
            self.processing_message = False

            self.start_initializer()

            subscriber = MQTTManager(self.mqtt_host, self.mqtt_port, self.client_id, False)
            subscriber.client.on_connect = self.on_connect
            subscriber.client.on_message = self.on_message

            subscriber.subscribe(self.subscription_topic)
        except Exception:
            print(traceback.format_exc())
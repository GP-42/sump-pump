#! /usr/bin/python3

from mqtt.exceptions import InvalidTopicError
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.configuration.classic.env_configuration import EnvConfiguration
from utilities.configuration.toml.toml_configuration import TomlConfiguration
from utilities.status import find, DeviceStatus, GeneralStatus, StatusLED

import blinkt
import threading
import time
import traceback

class MQTTSumpStatus(MQTTSubscriberBase):
    BLINK_INTERVAL = 1.5
    BRIGHTNESS = 0.1
    VALUE_ZERO = 0
    
    def __init__(self) -> None:
        self.TomlConfig = TomlConfiguration()
        self.EnvConfig = EnvConfiguration()
        super().__init__(self.TomlConfig.MQTTSumpStatus.host, self.TomlConfig.MQTTSumpStatus.port, self.EnvConfig.SumpStatusCredentials.MQTTUser, \
                         self.EnvConfig.SumpStatusCredentials.MQTTPassword, self.TomlConfig.MQTTSumpStatus.client_id, \
                         self.TomlConfig.MQTTSumpStatus.subscription_topic, self.TomlConfig.MQTTSumpStatus.message_qos)
        self.available_LEDs = []
        blinkt.set_clear_on_exit()
    
    def on_message_callback(self, client, userdata, message):
        status_value = str(message.payload.decode("utf-8"))
        LED_to_update = find(lambda status_led: status_led.name == self.get_last_subtopic(message.topic), self.available_LEDs)
        if LED_to_update is not None:
            LED_to_update.set_status(DeviceStatus[status_value])
            blinkt.set_pixel(LED_to_update.index, LED_to_update.current_status_color.r, LED_to_update.current_status_color.g, \
                            LED_to_update.current_status_color.b, self.VALUE_ZERO if (LED_to_update.current_status_color.r == self.VALUE_ZERO and \
                                LED_to_update.current_status_color.g == self.VALUE_ZERO and LED_to_update.current_status_color.b == self.VALUE_ZERO) else self.BRIGHTNESS)
            
            blinkt.show()
        else:
            raise InvalidTopicError(message.topic)
    
    def blink_pixels(self):
        try:
            while True:
                self.safe_to_proceed()
            
                self.processing_message = True
                
                LEDs_to_update = StatusLED.blink(self.available_LEDs)
                if len(LEDs_to_update) > 0:
                    for item in LEDs_to_update:
                        if item.current_LEDStatus == GeneralStatus.OFF:
                            blinkt.set_pixel(item.index, self.VALUE_ZERO, self.VALUE_ZERO, self.VALUE_ZERO, self.VALUE_ZERO)
                        else:
                            blinkt.set_pixel(item.index, item.current_status_color.r, item.current_status_color.g, item.current_status_color.b, self.BRIGHTNESS)
                    
                    blinkt.show()

                self.processing_message = False

                time.sleep(self.BLINK_INTERVAL)
        except Exception:
            print(traceback.format_exc())

    def start_initializer(self):
        self.available_LEDs = StatusLED.init_list()
        blink_thread = threading.Thread(target=self.blink_pixels, daemon=True)
        blink_thread.start()
    
if __name__ == '__main__':
    MQTTSumpStatus().start()
#! /usr/bin/python3

from mqtt.constants import Constants
from mqtt.mqtt_publisher_base import MQTTPublisherBase
from utilities.status import ButtonState

import buttonshim
import RPi.GPIO as gpio
import signal

class MQTTSumpButtons(MQTTPublisherBase):
    def __init__(self) -> None:
        super().__init__(Constants.MQTT_HOST, Constants.MQTT_PORT, "ButtonPublisher", "Sump/Command/Button/", 2)
        
        self.gpio_mode = gpio.BCM
        self.ledPin = 6
        self.buttonPin = 5
        
        gpio.setmode(self.gpio_mode)
        gpio.setup(self.ledPin, gpio.OUT)
        gpio.setup(self.buttonPin, gpio.IN, gpio.PUD_UP)
    
    def operations_button_callback(self, btn):
        button_pressed = gpio.input(self.buttonPin) == gpio.LOW
        global operationsButtonActivated
        operationsButtonActivated = button_pressed
        gpio.output(self.ledPin, button_pressed)
    
    def start(self):
        gpio.add_event_detect(self.buttonPin, gpio.BOTH, self.operations_button_callback)
        
        try:
            while True:
                signal.pause()
        finally:
            gpio.remove_event_detect(self.buttonPin)
            gpio.cleanup()
    
    def post_message_helper(self, index):
        global operationsButtonActivated
        if operationsButtonActivated:
            global button_actions
            self.post_message(f"{index}", f"{button_actions[index].name}", False)
    
    @buttonshim.on_press([buttonshim.BUTTON_A, buttonshim.BUTTON_B, buttonshim.BUTTON_C, buttonshim.BUTTON_D, buttonshim.BUTTON_E])
    def button_press(button, pressed):
        global button_actions
        button_actions[button] = ButtonState.PRESSED
    
    @buttonshim.on_release([buttonshim.BUTTON_A, buttonshim.BUTTON_B, buttonshim.BUTTON_C, buttonshim.BUTTON_D, buttonshim.BUTTON_E])
    def release_handler(button, pressed):
        global button_actions
        if button_actions[button].value != ButtonState.LONG_PRESS.value:
            button_actions[button] = ButtonState.SHORT_PRESS
            
            global MQTTSumpButtons_self
            MQTTSumpButtons_self.post_message_helper(button)
        
        button_actions[button] = ButtonState.NONE
    
    @buttonshim.on_hold([buttonshim.BUTTON_A, buttonshim.BUTTON_B, buttonshim.BUTTON_C, buttonshim.BUTTON_D, buttonshim.BUTTON_E], hold_time=3)
    def hold_handler(button):
        #print(f"{button}:{buttonshim._handlers[button].hold_time}")
        
        global button_actions
        button_actions[button] = ButtonState.LONG_PRESS
        
        global MQTTSumpButtons_self
        MQTTSumpButtons_self.post_message_helper(button)

MQTTSumpButtons_self = MQTTSumpButtons()
button_actions = [ButtonState.NONE, ButtonState.NONE, ButtonState.NONE, ButtonState.NONE, ButtonState.NONE]
operationsButtonActivated = False

if __name__ == '__main__':
    MQTTSumpButtons().start()
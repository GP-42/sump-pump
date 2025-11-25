#! /usr/bin/python3

from sump.utilities.generics import GenericJSONEncoder, GenericJSONDecoder
from sump.utilities.status import GeneralStatus

import RPi.GPIO as gpio

class Relay:
    def __init__(self, gpio_mode = gpio.BCM, gpio_pin = -1, general_status = GeneralStatus.OFF) -> None:
        if not isinstance(general_status, GeneralStatus):
            if isinstance(general_status, int):
                general_status = GeneralStatus(general_status)
            elif isinstance(general_status, str):
                general_status = GeneralStatus[general_status]
            else:
                raise TypeError("general_status must be an instance of GeneralStatus Enum")
        
        # GPIO Pin connected to relay
        self.gpio_mode = gpio_mode
        self.gpio_pin = gpio_pin
        self.general_status = general_status

        # # GPIO Mode (BOARD / BCM)
        # gpio.setmode(self.gpio_mode)

        # # set GPIO direction (IN / OUT)
        # gpio.setup(self.gpio_pin, gpio.OUT)
    
    def change_general_status(self, general_status) -> None:
        if not isinstance(general_status, GeneralStatus):
            if isinstance(general_status, int):
                general_status = GeneralStatus(general_status)
            elif isinstance(general_status, str):
                general_status = GeneralStatus[general_status]
            else:
                raise TypeError("general_status must be an instance of GeneralStatus Enum")
        
        self.general_status = general_status
    
    def switch_to_general_status(self) -> None:
        if self.general_status == GeneralStatus.ON:
            gpio.setwarnings(False)
        
        # GPIO Mode (BOARD / BCM)
        gpio.setmode(self.gpio_mode)

        # set GPIO direction (IN / OUT)
        gpio.setup(self.gpio_pin, gpio.OUT)
        
        value_to_set = gpio.LOW if self.general_status == GeneralStatus.ON else gpio.HIGH
        gpio.output(self.gpio_pin, value_to_set)

        if self.general_status == GeneralStatus.OFF:
            gpio.setwarnings(True)

class RelayEncoder(GenericJSONEncoder):
    _class = Relay

class RelayDecoder(GenericJSONDecoder):
    _class = Relay

class RelayModule:
    def __init__(self, gpio_mode = gpio.BCM, gpio_relay_pins = []) -> None:
        if type(gpio_relay_pins) is not list:
            gpio_relay_pins = [ gpio_relay_pins ]
        
        self.gpio_relays = []

        for item in gpio_relay_pins:
            relay = Relay(gpio_mode, item)
            self.gpio_relays.append(relay)
    
    def __getitem__(self, relay_index):
        if relay_index < len(self.gpio_relays):
            return self.gpio_relays[relay_index]
        else:
            raise IndexError("list index out of range")
    
    def change_general_status(self, relay_index, general_status) -> None:
        self[relay_index].change_general_status(general_status)
    
    def switch_to_general_status(self, relay_index) -> None:
        self[relay_index].switch_to_general_status()
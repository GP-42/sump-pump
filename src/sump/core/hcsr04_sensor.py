#! /usr/bin/python3

import RPi.GPIO as gpio
import time

class Hcsr04Sensor:
    def __init__(self, gpio_mode, gpio_trigger, gpio_echo) -> None:
        # GPIO Pins connected to sensor
        self.gpio_mode = gpio_mode
        self.gpio_trigger = gpio_trigger
        self.gpio_echo = gpio_echo

        # GPIO Mode (BOARD / BCM)
        gpio.setmode(self.gpio_mode)

        # set GPIO direction (IN / OUT)
        gpio.setup(self.gpio_trigger, gpio.OUT)
        gpio.setup(self.gpio_echo, gpio.IN)

    def distance(self) -> float:
        # return random.random() * 5 + 30

        time.sleep(3)

        # set Trigger to HIGH
        gpio.output(self.gpio_trigger, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        gpio.output(self.gpio_trigger, False)

        StartTime = time.time()
        StopTime = time.time()

        # save StartTime (after start of echo pulse)
        while gpio.input(self.gpio_echo) == 0:
            StartTime = time.time()

        # save time of arrival
        while gpio.input(self.gpio_echo) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2

        return distance
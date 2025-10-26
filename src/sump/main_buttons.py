#! /usr/bin/python3

from main_helper import MainHelper
from mqtt.mqtt_sump_buttons import MQTTSumpButtons
from pathlib import Path

if __name__ == '__main__':
    MainHelper(Path(__file__).name).run(MQTTSumpButtons)
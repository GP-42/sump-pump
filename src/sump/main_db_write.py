#! /usr/bin/python3

from main_helper import MainHelper
from mqtt.mqtt_sump_db_write import MQTTSumpDBWrite
from pathlib import Path

if __name__ == '__main__':
    MainHelper(Path(__file__).name).run(MQTTSumpDBWrite)
#! /usr/bin/python3

from main_helper import MainHelper
from mqtt.mqtt_sump_tank_watcher import MQTTSumpTankWatcher
from pathlib import Path

if __name__ == '__main__':
    MainHelper(Path(__file__).name).run(MQTTSumpTankWatcher)
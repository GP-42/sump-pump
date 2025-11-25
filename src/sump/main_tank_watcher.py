#! /usr/bin/python3

from pathlib import Path
from sump.main_helper import MainHelper
from sump.mqtt.mqtt_sump_tank_watcher import MQTTSumpTankWatcher

if __name__ == '__main__':
    MainHelper(Path(__file__).name).run(MQTTSumpTankWatcher)
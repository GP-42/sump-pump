#! /usr/bin/python3

from main_helper import MainHelper
from mqtt.mqtt_sump_status import MQTTSumpStatus
from pathlib import Path

import traceback

if __name__ == '__main__':
    MainHelper(Path(__file__).name).run(MQTTSumpStatus)
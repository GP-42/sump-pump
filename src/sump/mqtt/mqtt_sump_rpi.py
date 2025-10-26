#! /usr/bin/python3

from mqtt.constants import Constants
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.status import DeviceStatus

import subprocess

class MQTTSumpRPi(MQTTSubscriberBase):
    def __init__(self) -> None:
        super().__init__(Constants.MQTT_HOST, Constants.MQTT_PORT, "RPiSubscriber", "Sump/RPi", 2)
    
    def on_message_callback(self, client, userdata, message):
        status = DeviceStatus[str(message.payload.decode("utf-8"))]
        shutdown_command = "sudo shutdown".split()

        match status:
            case DeviceStatus.CANCELED:
                shutdown_command.append("-c")
                shutdown_command.append('"Reboot / Shutdown cancelled via button."')
                subprocess.run(shutdown_command)
            case DeviceStatus.REBOOT:
                shutdown_command.append("-r")
                shutdown_command.append("+3")
                shutdown_command.append('"Reboot initiated via button."')
                subprocess.run(shutdown_command)
            case DeviceStatus.SHUTDOWN:
                shutdown_command.append("-h")
                shutdown_command.append("+3")
                shutdown_command.append('"Shutdown initiated via button."')
                subprocess.run(shutdown_command)

if __name__ == '__main__':
    MQTTSumpRPi().start()
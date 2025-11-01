#! /usr/bin/python3

from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.configuration.toml.toml_configuration import TomlConfiguration
from utilities.status import DeviceStatus

import subprocess

class MQTTSumpRPi(MQTTSubscriberBase):
    def __init__(self) -> None:
        self.config = TomlConfiguration()
        super().__init__(self.config.MQTTSumpRPi.host, self.config.MQTTSumpRPi.port, self.config.MQTTSumpRPi.client_id, self.config.MQTTSumpRPi.subscription_topic, self.config.MQTTSumpRPi.message_qos)
    
    def on_message_callback(self, client, userdata, message):
        status = DeviceStatus[str(message.payload.decode("utf-8"))]
        shutdown_command = "sudo shutdown".split()

        match status:
            case DeviceStatus.CANCELED:
                shutdown_command.append("-c")
                shutdown_command.append('"Reboot / Shutdown canceled via button."')
                subprocess.run(shutdown_command)
            case DeviceStatus.REBOOT:
                shutdown_command.append("-r")
                shutdown_command.append(f"+{self.config.MQTTSumpRPi.reboot_shutdown_delay}")
                shutdown_command.append('"Reboot initiated via button."')
                subprocess.run(shutdown_command)
            case DeviceStatus.SHUTDOWN:
                shutdown_command.append("-h")
                shutdown_command.append(f"+{self.config.MQTTSumpRPi.reboot_shutdown_delay}")
                shutdown_command.append('"Shutdown initiated via button."')
                subprocess.run(shutdown_command)

if __name__ == '__main__':
    MQTTSumpRPi().start()
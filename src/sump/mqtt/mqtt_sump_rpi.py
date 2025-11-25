#! /usr/bin/python3

from sump.mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from sump.utilities.configuration.classic.env_configuration import EnvConfiguration
from sump.utilities.configuration.toml.toml_configuration import TomlConfiguration
from sump.utilities.status import DeviceStatus

import subprocess

class MQTTSumpRPi(MQTTSubscriberBase):
    def __init__(self) -> None:
        self.TomlConfig = TomlConfiguration()
        self.EnvConfig = EnvConfiguration()
        super().__init__(self.TomlConfig.MQTTSumpRPi.host, self.TomlConfig.MQTTSumpRPi.port, self.EnvConfig.SumpRPiCredentials.MQTTUser, \
                         self.EnvConfig.SumpRPiCredentials.MQTTPassword, self.TomlConfig.MQTTSumpRPi.client_id, \
                         self.TomlConfig.MQTTSumpRPi.subscription_topic, self.TomlConfig.MQTTSumpRPi.message_qos)
    
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
                shutdown_command.append(f"+{self.TomlConfig.MQTTSumpRPi.reboot_shutdown_delay}")
                shutdown_command.append('"Reboot initiated via button."')
                subprocess.run(shutdown_command)
            case DeviceStatus.SHUTDOWN:
                shutdown_command.append("-h")
                shutdown_command.append(f"+{self.TomlConfig.MQTTSumpRPi.reboot_shutdown_delay}")
                shutdown_command.append('"Shutdown initiated via button."')
                subprocess.run(shutdown_command)

if __name__ == '__main__':
    MQTTSumpRPi().start()
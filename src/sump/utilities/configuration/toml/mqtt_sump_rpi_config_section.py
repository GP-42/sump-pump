#! /usr/bin/python3

from utilities.configuration.toml.mqtt_pure_subscriber_config_section_base import MQTTPureSubscriberConfigSectionBase

class MQTTSumpRPiConfigSection(MQTTPureSubscriberConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "MQTTSumpRPi")
    
    @property
    def reboot_shutdown_delay(self):
        return int(self.toml_config.get(self.config_section).get("reboot_shutdown_delay"))
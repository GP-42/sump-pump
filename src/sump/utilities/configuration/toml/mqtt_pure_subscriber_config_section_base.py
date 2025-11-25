#! /usr/bin/python3

from sump.utilities.configuration.toml.mqtt_config_section_base import MQTTConfigSectionBase

class MQTTPureSubscriberConfigSectionBase(MQTTConfigSectionBase):
    def __init__(self, toml_config, section_name) -> None:
        super().__init__(toml_config, section_name)
    
    @property
    def subscription_topic(self):
        return self.toml_config.get(self.config_section).get("subscription_topic")
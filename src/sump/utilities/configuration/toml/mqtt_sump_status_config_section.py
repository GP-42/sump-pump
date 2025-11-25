#! /usr/bin/python3

from sump.utilities.configuration.toml.mqtt_pure_subscriber_config_section_base import MQTTPureSubscriberConfigSectionBase

class MQTTSumpStatusConfigSection(MQTTPureSubscriberConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "MQTTSumpStatus")
#! /usr/bin/python3

from utilities.configuration.toml.mqtt_pure_publisher_config_section_base import MQTTPurePublisherConfigSectionBase

class MQTTSumpButtonsConfigSection(MQTTPurePublisherConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "MQTTSumpButtons")
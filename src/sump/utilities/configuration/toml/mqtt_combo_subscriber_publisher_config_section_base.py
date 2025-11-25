#! /usr/bin/python3

from sump.utilities.configuration.toml.mqtt_pure_subscriber_config_section_base import MQTTPureSubscriberConfigSectionBase
from sump.utilities.configuration.toml.mqtt_pure_publisher_config_section_base import MQTTPurePublisherConfigSectionBase

class MQTTComboSubscriberPublisherConfigSectionBase(MQTTPureSubscriberConfigSectionBase, MQTTPurePublisherConfigSectionBase):
    def __init__(self, toml_config, section_name) -> None:
        super().__init__(toml_config, section_name)
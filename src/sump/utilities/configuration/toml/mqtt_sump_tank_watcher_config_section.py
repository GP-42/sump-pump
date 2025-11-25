#! /usr/bin/python3

from sump.utilities.configuration.toml.mqtt_combo_subscriber_publisher_config_section_base import MQTTComboSubscriberPublisherConfigSectionBase

class MQTTSumpTankWatcherConfigSection(MQTTComboSubscriberPublisherConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "MQTTSumpTankWatcher")
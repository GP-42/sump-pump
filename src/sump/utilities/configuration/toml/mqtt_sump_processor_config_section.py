#! /usr/bin/python3

from sump.utilities.configuration.toml.mqtt_combo_subscriber_publisher_config_section_base import MQTTComboSubscriberPublisherConfigSectionBase

class MQTTSumpProcessorConfigSection(MQTTComboSubscriberPublisherConfigSectionBase):
    def __init__(self, toml_config) -> None:
        super().__init__(toml_config, "MQTTSumpProcessor")
    
    @property
    def reboot_shutdown_timer_no_return(self):
        return int(self.toml_config.get(self.config_section).get("reboot_shutdown_timer_no_return"))
    
    @property
    def confirmation_timer_duration(self):
        return int(self.toml_config.get(self.config_section).get("confirmation_timer_duration"))
    
    @property
    def confirmation_delay(self):
        return int(self.toml_config.get(self.config_section).get("confirmation_delay"))
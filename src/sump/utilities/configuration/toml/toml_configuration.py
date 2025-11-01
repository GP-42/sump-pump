#! /usr/bin/python3

from utilities.configuration.configuration_base import ConfigurationBase
from utilities.configuration.toml.hcsr04_sensor_config_section import Hcsr04SensorConfigSection
from utilities.configuration.toml.mqtt_sump_buttons_config_section import MQTTSumpButtonsConfigSection
from utilities.configuration.toml.mqtt_sump_db_write_config_section import MQTTSumpDBWriteConfigSection
from utilities.configuration.toml.mqtt_sump_processor_config_section import MQTTSumpProcessorConfigSection
from utilities.configuration.toml.mqtt_sump_relay_config_section import MQTTSumpRelayConfigSection
from utilities.configuration.toml.mqtt_sump_rpi_config_section import MQTTSumpRPiConfigSection
from utilities.configuration.toml.mqtt_sump_status_config_section import MQTTSumpStatusConfigSection
from utilities.configuration.toml.mqtt_sump_tank_watcher_config_section import MQTTSumpTankWatcherConfigSection
from utilities.configuration.toml.relay_module_config_section import RelayModuleConfigSection
from utilities.configuration.toml.sump_operations_config_section import SumpOperationsConfigSection
from utilities.configuration.toml.tank_watcher_config_section import TankWatcherConfigSection

import tomllib

class TomlConfiguration(ConfigurationBase):
    def __init__(self) -> None:
        super().__init__()
        self._Hcsr04SensorSection = Hcsr04SensorConfigSection(self)
        self._TankWatcherSection = TankWatcherConfigSection(self)
        self._SumpOperationsSection = SumpOperationsConfigSection(self)
        self._RelayModuleSection = RelayModuleConfigSection(self)
        self._MQTTSumpProcessorSection = MQTTSumpProcessorConfigSection(self)
        self._MQTTSumpStatusSection = MQTTSumpStatusConfigSection(self)
        self._MQTTSumpDBWriteSection = MQTTSumpDBWriteConfigSection(self)
        self._MQTTSumpRPiSection = MQTTSumpRPiConfigSection(self)
        self._MQTTSumpTankWatcherSection = MQTTSumpTankWatcherConfigSection(self)
        self._MQTTSumpRelaySection = MQTTSumpRelayConfigSection(self)
        self._MQTTSumpButtonsSection = MQTTSumpButtonsConfigSection(self)
    
    def reload(self):
        try:
            with open("../../config/sump-pump.toml", "rb") as f:
                self.config = tomllib.load(f)
        except FileNotFoundError:
            print(f"Config file not found, using defaults")
            return {}
        except tomllib.TOMLDecodeError as e:
            print(f"Error parsing TOML: {e}")
            raise
    
    def get(self, key, default=None):
        """Get a top-level configuration value"""
        return self.config.get(key, default)

    def get_section(self, section):
        """Get an entire configuration section"""
        if section not in self.config:
            raise ValueError(f"Section '{section}' not found")
        return self.config[section]

    @property
    def Hcsr04Sensor(self):
        return self._Hcsr04SensorSection
    
    @property
    def TankWatcher(self):
        return self._TankWatcherSection
    
    @property
    def SumpOperations(self):
        return self._SumpOperationsSection
    
    @property
    def RelayModule(self):
        return self._RelayModuleSection
    
    @property
    def MQTTSumpProcessor(self):
        return self._MQTTSumpProcessorSection
    
    @property
    def MQTTSumpStatus(self):
        return self._MQTTSumpStatusSection
    
    @property
    def MQTTSumpDBWrite(self):
        return self._MQTTSumpDBWriteSection
    
    @property
    def MQTTSumpRPi(self):
        return self._MQTTSumpRPiSection
    
    @property
    def MQTTSumpTankWatcher(self):
        return self._MQTTSumpTankWatcherSection
    
    @property
    def MQTTSumpRelay(self):
        return self._MQTTSumpRelaySection
    
    @property
    def MQTTSumpButtons(self):
        return self._MQTTSumpButtonsSection
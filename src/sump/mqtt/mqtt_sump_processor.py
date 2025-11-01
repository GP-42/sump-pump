#! /usr/bin/python3

from core.relay_module import RelayEncoder, RelayModule
from mqtt.exceptions import InvalidTopicError
from mqtt.mqtt_publisher_base import MQTTPublisherBase
from mqtt.mqtt_subscriber_base import MQTTSubscriberBase
from utilities.configuration.classic.env_configuration import EnvConfiguration
from utilities.configuration.toml.toml_configuration import TomlConfiguration
from utilities.status import ButtonState, DeviceStatus, GeneralStatus, LEDnames, SystemStatus, SystemStatusItemEncoder

import json
import RPi.GPIO as gpio
import threading
import time

class MQTTSumpProcessor(MQTTSubscriberBase, MQTTPublisherBase):
    def __init__(self) -> None:
        self.TomlConfig = TomlConfiguration()
        self.EnvConfig = EnvConfiguration()
        super().__init__(self.TomlConfig.MQTTSumpProcessor.host, self.TomlConfig.MQTTSumpProcessor.port, self.EnvConfig.SumpProcessorCredentials.MQTTUser, \
                         self.EnvConfig.SumpProcessorCredentials.MQTTPassword, self.TomlConfig.MQTTSumpProcessor.client_id, \
                         self.TomlConfig.MQTTSumpProcessor.subscription_topic, self.TomlConfig.MQTTSumpProcessor.message_qos)
        self.publisher_root_topic = self.TomlConfig.MQTTSumpProcessor.publisher_root_topic
        self.system_status = SystemStatus()
        self.initialize_system_status()
        self.timed_status = DeviceStatus.get_status_requiring_confirmation()
        self.active_timers = {}
        self.relay_module = RelayModule(self.TomlConfig.RelayModule.gpio_mode, self.TomlConfig.RelayModule.gpio_pins)
    
    def on_message_callback(self, client, userdata, message):
        # print(f"Message topic: {message.topic}")
        # print(f"Contents: {str(message.payload.decode("utf-8"))}")
        topic_parts = self.split_topic(message.topic)
        match topic_parts[2]:
            case "Button":
                status_value = ButtonState[str(message.payload.decode("utf-8"))]

                match topic_parts[3]:
                    case "0":
                        if not self.confirmation_delay_is_active(self.system_status.reboot_shutdown):
                            match status_value:
                                case ButtonState.SHORT_PRESS:
                                    match self.system_status.reboot_shutdown.current_status:
                                        case DeviceStatus.REBOOT_TO_CONFIRM:
                                            self.start_timer_and_post(self.system_status.reboot_shutdown, DeviceStatus.REBOOT, True)
                                        case DeviceStatus.SHUTDOWN_TO_CONFIRM:
                                            self.start_timer_and_post(self.system_status.reboot_shutdown, DeviceStatus.SHUTDOWN, True)
                                case ButtonState.LONG_PRESS:
                                    match self.system_status.reboot_shutdown.current_status:
                                        case DeviceStatus.NONE:
                                            self.start_timer_and_post(self.system_status.reboot_shutdown, DeviceStatus.REBOOT_TO_CONFIRM)
                                        case DeviceStatus.REBOOT_TO_CONFIRM:
                                            self.start_timer_and_post(self.system_status.reboot_shutdown, DeviceStatus.SHUTDOWN_TO_CONFIRM, True)
                                        case DeviceStatus.SHUTDOWN_TO_CONFIRM | DeviceStatus.REBOOT | DeviceStatus.SHUTDOWN:
                                            self.stop_timer_and_cancel(self.system_status.reboot_shutdown)
                    case "1":
                        self.enable_disable_auto(status_value, self.system_status.sensor_auto)
                    case "2":
                        self.start_stop_manual(status_value, self.system_status.sensor_manual, self.system_status.sensor_auto)
                    case "3":
                        self.enable_disable_auto(status_value, self.system_status.relay_auto)
                    case "4":
                        self.start_stop_manual(status_value, self.system_status.relay_manual, self.system_status.relay_auto)
                    case _:
                        raise InvalidTopicError(message.topic)
            case "App":
                match topic_parts[3]:
                    case LEDnames.SENSOR_AUTO | LEDnames.SENSOR_MANUAL:
                        system_status_item = self.system_status.__getattribute__(topic_parts[3].lower())
                        
                        if self.system_status.sensor_error.current_status == DeviceStatus.NONE:                            
                            status_value = DeviceStatus[str(message.payload.decode("utf-8"))]
                            self.change_status_and_post(system_status_item, status_value)
                    case LEDnames.SENSOR_ERROR | LEDnames.RELAY_ERROR:
                        pass
                    case "Measurement":
                        if self.system_status.relay_error.current_status == DeviceStatus.NONE:
                            water_depth = float(str(message.payload.decode("utf-8")))

                            if water_depth >= self.system_status.PUMP_START_DEPTH:
                                if self.system_status.relay_auto.current_status != DeviceStatus.WORKING \
                                and self.system_status.relay_manual.current_status != DeviceStatus.WORKING:
                                    self.change_status_and_post(self.system_status.relay_auto, DeviceStatus.WORKING)
                                
                                self.change_status_and_post(self.system_status.sensor_auto, DeviceStatus.WORKING)
                            elif water_depth < self.system_status.PUMP_START_DEPTH and water_depth > self.system_status.PUMP_STOP_DEPTH:
                                if self.system_status.relay_auto.current_status == DeviceStatus.WORKING \
                                or self.system_status.relay_manual.current_status == DeviceStatus.WORKING:
                                    self.change_status_and_post(self.system_status.sensor_auto, DeviceStatus.WORKING)
                            elif water_depth <= self.system_status.PUMP_STOP_DEPTH:
                                if self.system_status.relay_auto.current_status == DeviceStatus.WORKING:
                                    self.change_status_and_post(self.system_status.relay_auto, DeviceStatus.STOP_WORKING)
                                elif self.system_status.relay_manual.current_status == DeviceStatus.WORKING:
                                    self.change_status_and_post(self.system_status.relay_manual, DeviceStatus.STOP_WORKING)
                    case _:
                        raise InvalidTopicError(message.topic)
            case _:
                raise InvalidTopicError(message.topic)
    
    def enable_disable_auto(self, status_value, system_status_item):
        if not self.confirmation_delay_is_active(system_status_item):
            match status_value:
                case ButtonState.SHORT_PRESS:
                    match system_status_item.current_status:
                        case DeviceStatus.DISABLE_TO_CONFIRM:
                            self.stop_timer_and_post(system_status_item, DeviceStatus.DISABLED)
                        case DeviceStatus.ENABLE_TO_CONFIRM:
                            self.stop_timer_and_post(system_status_item, DeviceStatus.ENABLED)
                case ButtonState.LONG_PRESS:
                    match system_status_item.current_status:
                        case DeviceStatus.ENABLED:
                            self.start_timer_and_post(system_status_item, DeviceStatus.DISABLE_TO_CONFIRM)
                        case DeviceStatus.DISABLED:
                            self.start_timer_and_post(system_status_item, DeviceStatus.ENABLE_TO_CONFIRM)
                        case DeviceStatus.DISABLE_TO_CONFIRM | DeviceStatus.ENABLE_TO_CONFIRM:
                            self.stop_timer_and_cancel(system_status_item)
    
    def start_stop_manual(self, status_value, system_status_item_manual, system_status_item_auto):
        if not self.confirmation_delay_is_active(system_status_item_manual):
            match status_value:
                case ButtonState.SHORT_PRESS:
                    match system_status_item_manual.current_status:
                        case DeviceStatus.MANUAL_TO_CONFIRM:
                            if system_status_item_auto.current_status != DeviceStatus.WORKING:
                                self.stop_timer_and_post(system_status_item_manual, DeviceStatus.WORKING)
                            else:
                                self.stop_timer_and_cancel(system_status_item_manual)
                        case DeviceStatus.STOP_TO_CONFIRM:
                            self.stop_timer_and_post(system_status_item_manual, DeviceStatus.STOP_WORKING)
                case ButtonState.LONG_PRESS:
                    match system_status_item_manual.current_status:
                        case DeviceStatus.NONE:
                            if system_status_item_auto.current_status != DeviceStatus.WORKING:
                                self.start_timer_and_post(system_status_item_manual, DeviceStatus.MANUAL_TO_CONFIRM)
                        case DeviceStatus.MANUAL_TO_CONFIRM:
                            self.stop_timer_and_cancel(system_status_item_manual)
                        case DeviceStatus.WORKING:
                            self.start_timer_and_post(system_status_item_manual, DeviceStatus.STOP_TO_CONFIRM)
    
    def confirmation_delay_is_active(self, system_status_item) -> bool:
        delay_is_active = False
        
        if system_status_item.name in self.active_timers:
            start_time, timer_thread, stop_event = self.active_timers.get(system_status_item.name, (None, None, None))
            delay_is_active = time.time() - start_time < self.TomlConfig.MQTTSumpProcessor.confirmation_delay
        
        return delay_is_active
    
    def change_status_and_post(self, system_status_item, device_status):
        system_status_item.change_status(device_status, False)
        self.post_messages(system_status_item)
    
    def start_timer_and_post(self, system_status_item, device_status, stop_previous_timer = False):
        system_status_item.change_status(device_status, False)
        if stop_previous_timer:
            self.stop_timer(system_status_item)
        self.start_timer(system_status_item)
        self.post_messages(system_status_item)
    
    def stop_timer_and_post(self, system_status_item, device_status):
        system_status_item.change_status(device_status, False)
        self.stop_timer(system_status_item)
        self.post_messages(system_status_item)
    
    def stop_timer_and_cancel(self, system_status_item):
        self.stop_timer(system_status_item)
        self.cancel_action_and_post(system_status_item)
    
    def timer(self, system_status_item, stop_event, start_time):
        while time.time() - start_time < self.TomlConfig.MQTTSumpProcessor.confirmation_timer_duration:
            if stop_event.is_set():
                return
            time.sleep(0.1)
        
        self.cancel_action_and_post(system_status_item)
            
        del self.active_timers[system_status_item.name]
    
    def reboot_shutdown_timer(self, system_status_item, stop_event, start_time):
        while time.time() - start_time < self.TomlConfig.MQTTSumpProcessor.reboot_shutdown_timer_no_return:
            if stop_event.is_set():
                return
            time.sleep(0.1)
        
        self.neutralize_action_and_post(system_status_item)
        self.system_status.set_all(DeviceStatus.NONE)
        self.update_all_LEDs()

        del self.active_timers[system_status_item.name]

    def is_timer_for_reboot_shutdown(self, system_status_item):
        return (system_status_item.name == LEDnames.REBOOT_SHUTDOWN) and (system_status_item.current_status in DeviceStatus.REBOOT | DeviceStatus.SHUTDOWN)
    
    def start_timer(self, system_status_item):
        start_time = time.time()
        stop_event = threading.Event()
        timer_thread = threading.Thread(target=self.reboot_shutdown_timer, args=(system_status_item, stop_event, start_time)) \
            if self.is_timer_for_reboot_shutdown(system_status_item) \
            else threading.Thread(target=self.timer, args=(system_status_item, stop_event, start_time))
        self.active_timers[system_status_item.name] = (start_time, timer_thread, stop_event)
        timer_thread.start()

    def stop_timer(self, system_status_item):
        start_time, timer_thread, stop_event = self.active_timers.get(system_status_item.name, (None, None, None))
        if timer_thread and timer_thread.is_alive():
            stop_event.set()
            timer_thread.join()
        
        del self.active_timers[system_status_item.name]

    def stop_action_and_post(self, system_status_item):
        self.change_status_and_post(system_status_item, DeviceStatus.STOP_WORKING)

    def cancel_action_and_post(self, system_status_item):
        self.change_status_and_post(system_status_item, DeviceStatus.CANCELED)
    
    def neutralize_action_and_post(self, system_status_item):
        self.change_status_and_post(system_status_item, DeviceStatus.NONE)
    
    def post_messages(self, system_status_item):
        status_is_for_reset = system_status_item.current_status in DeviceStatus.get_status_for_reset()
        
        if status_is_for_reset:
            self.post_message_DB(system_status_item)
        else:
            self.post_message_LED(system_status_item)

        if system_status_item.name == LEDnames.REBOOT_SHUTDOWN:
            self.post_message_rpi(system_status_item)
        
        if system_status_item.name.startswith("SENSOR_"):
            match system_status_item.current_status:
                case DeviceStatus.WORKING:
                    self.post_message_sensor(system_status_item)
        
        if system_status_item.name.startswith("RELAY_"):
            match system_status_item.current_status:
                case DeviceStatus.WORKING:
                    self.post_message_relay(0, GeneralStatus.ON)
                case DeviceStatus.STOP_WORKING:
                    self.post_message_relay(0, GeneralStatus.OFF)
        
        if status_is_for_reset:
            system_status_item.change_status(system_status_item.current_status, True)
            self.post_message_LED(system_status_item)
        
        self.post_message_DB(system_status_item)
    
    def post_message_LED(self, system_status_item):
        self.post_message(f"LED/{system_status_item.name}", f"{system_status_item.current_status.name}", True)
    
    def post_message_rpi(self, system_status_item):
        self.post_message(f"RPi", f"{system_status_item.current_status.name}", False)

    def post_message_sensor(self, system_status_item):
        self.post_message(f"Sensor/{system_status_item.name}", f"{system_status_item.current_status.name}", False)
    
    def post_message_relay(self, relay_index, general_status):
        self.relay_module.change_general_status(relay_index, general_status)
        converted = json.dumps(self.relay_module[relay_index], cls=RelayEncoder)
        self.post_message("Relay", converted, False)
    
    def post_message_DB(self, system_status_item):
        converted = json.dumps(system_status_item, cls=SystemStatusItemEncoder)
        self.post_message("DB/SystemStatusItem", converted, False)
    
    def update_all_LEDs(self):
        self.post_message_LED(self.system_status.rpi)
        self.post_message_LED(self.system_status.reboot_shutdown)
        self.post_message_LED(self.system_status.sensor_auto)
        self.post_message_LED(self.system_status.sensor_manual)
        self.post_message_LED(self.system_status.sensor_error)
        self.post_message_LED(self.system_status.relay_auto)
        self.post_message_LED(self.system_status.relay_manual)
        self.post_message_LED(self.system_status.relay_error)
    
    def initialize_system_status(self):        
        self.system_status.load_from_db()
        self.update_all_LEDs()

if __name__ == '__main__':
    MQTTSumpProcessor().start()
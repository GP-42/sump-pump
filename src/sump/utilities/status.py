#! /usr/bin/python3

from contextlib import closing
from enum import Enum, Flag
from functools import total_ordering
from utilities.formatters import get_formatted_now
from utilities.generics import GenericJSONEncoder, GenericJSONDecoder
from utilities.sequences import find

import utilities.sqlite3db as db

class ButtonState(Enum):
    NONE = 0
    PRESSED = 1
    SHORT_PRESS = 2
    LONG_PRESS = 3

class LEDnames():
    RPI = "RPI"
    REBOOT_SHUTDOWN = "REBOOT_SHUTDOWN"
    SENSOR_AUTO = "SENSOR_AUTO"
    SENSOR_MANUAL = "SENSOR_MANUAL"
    SENSOR_ERROR = "SENSOR_ERROR"
    RELAY_AUTO = "RELAY_AUTO"
    RELAY_MANUAL = "RELAY_MANUAL"
    RELAY_ERROR = "RELAY_ERROR"

class LEDFunction(Enum):
    SOLID = 0
    BLINK = 1

class GeneralStatus(Enum):
    OFF = 0
    ON = 1

class DeviceStatus(Flag):
    INVALID = 0
    NONE = 1
    POWERED_AND_ONLINE = 2
    POWERED_NO_NETWORK = 4
    ERROR = 8
    ENABLED = 16
    WORKING = 32
    DISABLE_TO_CONFIRM = 64
    DISABLED = 128
    ENABLE_TO_CONFIRM = 256
    RESET_ERROR = 512 # No LED required
    MANUAL_TO_CONFIRM = 1024
    CANCELED = 2048 # No LED required
    STOP_WORKING = 4096 # No LED required
    REBOOT_TO_CONFIRM = 8192
    REBOOT = 16384
    SHUTDOWN_TO_CONFIRM = 32768
    SHUTDOWN = 65536
    STOP_TO_CONFIRM = 131072
    
    def __add__(self, other):
        if isinstance(other, DeviceStatus):
            return self.value + other.value
        elif isinstance(other, int) or isinstance(other, float):
            return self.value + other
        else:
            raise TypeError("Unsupported operand type(s) for +")
    
    def __iadd__(self, other):
        if isinstance(other, DeviceStatus):
            return self.value + other.value
        elif isinstance(other, int) or isinstance(other, float):
            return self.value + other
        else:
            raise TypeError("Unsupported operand type(s) for +=")

    def __radd__(self, other):
        return self.__add__(other)
    
    @staticmethod
    def get_status_requiring_confirmation():
        return DeviceStatus.DISABLE_TO_CONFIRM | DeviceStatus.ENABLE_TO_CONFIRM | DeviceStatus.MANUAL_TO_CONFIRM | DeviceStatus.REBOOT_TO_CONFIRM \
            | DeviceStatus.SHUTDOWN_TO_CONFIRM | DeviceStatus.STOP_TO_CONFIRM
    
    @staticmethod
    def get_status_for_reset():
        return DeviceStatus.RESET_ERROR | DeviceStatus.CANCELED | DeviceStatus.STOP_WORKING
    
    @staticmethod
    def get_acknowledged_status():
        return DeviceStatus.NONE | DeviceStatus.ERROR | DeviceStatus.ENABLED | DeviceStatus.WORKING | DeviceStatus.DISABLED \
            | DeviceStatus.REBOOT | DeviceStatus.SHUTDOWN

@total_ordering
class StatusColor():
    def __init__(self, status, r, g, b, led_function) -> None:
        if not isinstance(status, DeviceStatus):
            raise TypeError("status must be an instance of DeviceStatus Enum")
        if not isinstance(led_function, LEDFunction):
            raise TypeError("led_function must be an instance of LEDFunction Enum")
        
        self.status = status
        self.r = r
        self.g = g
        self.b = b
        self.led_function = led_function
    
    def __lt__(self, obj):
        if not isinstance(obj, StatusColor):
            raise TypeError("obj must be an instance of StatusColor")
        
        return ((self.status.value) < (obj.status.value))
  
    def __gt__(self, obj):
        if not isinstance(obj, StatusColor):
            raise TypeError("obj must be an instance of StatusColor")
        
        return ((self.status.value) > (obj.status.value))
  
    def __le__(self, obj):
        if not isinstance(obj, StatusColor):
            raise TypeError("obj must be an instance of StatusColor")
        
        return ((self.status.value) <= (obj.status.value))
  
    def __ge__(self, obj):
        if not isinstance(obj, StatusColor):
            raise TypeError("obj must be an instance of StatusColor")
        
        return ((self.status.value) >= (obj.status.value))
  
    def __eq__(self, obj):
        if not isinstance(obj, StatusColor):
            raise TypeError("obj must be an instance of StatusColor")
        
        return (self.status.value == obj.status.value)
    
    def __str__(self) -> str:
        return f"StatusColor {self.status.name} has R: {self.r}, G: {self.g}, B: {self.b} and is configured with LEDFunction {self.led_function.name}."
    
    def __repr__(self) -> str:
        return f"StatusColor({str(self.status)}, {self.r}, {self.g}, {self.b}, {str(self.led_function)})"
    
    @staticmethod
    def get_list():
        status_NONE = StatusColor(DeviceStatus.NONE, 0, 0, 0, LEDFunction.SOLID)
        status_POWERED_AND_ONLINE = StatusColor(DeviceStatus.POWERED_AND_ONLINE, 0, 100, 0, LEDFunction.SOLID)
        status_POWERED_NO_NETWORK = StatusColor(DeviceStatus.POWERED_NO_NETWORK, 255, 140, 0, LEDFunction.BLINK)
        status_ERROR = StatusColor(DeviceStatus.ERROR, 255, 0, 0, LEDFunction.BLINK)
        status_ENABLED = StatusColor(DeviceStatus.ENABLED, 0, 100, 0, LEDFunction.SOLID)
        status_WORKING = StatusColor(DeviceStatus.WORKING, 0, 0, 255, LEDFunction.BLINK)
        status_DISABLE_TO_CONFIRM = StatusColor(DeviceStatus.DISABLE_TO_CONFIRM, 255, 140, 0, LEDFunction.BLINK)
        status_DISABLED = StatusColor(DeviceStatus.DISABLED, 255, 0, 0, LEDFunction.SOLID)
        status_ENABLE_TO_CONFIRM = StatusColor(DeviceStatus.ENABLE_TO_CONFIRM, 0, 100, 0, LEDFunction.BLINK)
        status_MANUAL_TO_CONFIRM = StatusColor(DeviceStatus.MANUAL_TO_CONFIRM, 0, 100, 0, LEDFunction.BLINK)
        status_REBOOT_TO_CONFIRM = StatusColor(DeviceStatus.REBOOT_TO_CONFIRM, 255, 140, 0, LEDFunction.BLINK)
        status_REBOOT = StatusColor(DeviceStatus.REBOOT, 255, 140, 0, LEDFunction.SOLID)
        status_SHUTDOWN_TO_CONFIRM = StatusColor(DeviceStatus.SHUTDOWN_TO_CONFIRM, 255, 0, 0, LEDFunction.BLINK)
        status_SHUTDOWN = StatusColor(DeviceStatus.SHUTDOWN, 255, 0, 0, LEDFunction.SOLID)
        status_STOP_TO_CONFIRM = StatusColor(DeviceStatus.STOP_TO_CONFIRM, 255, 140, 0, LEDFunction.BLINK)

        statusColors = [
            status_NONE, status_POWERED_AND_ONLINE, status_POWERED_NO_NETWORK, status_ERROR,
            status_ENABLED, status_WORKING, status_DISABLE_TO_CONFIRM, status_DISABLED, status_ENABLE_TO_CONFIRM,
            status_MANUAL_TO_CONFIRM, status_REBOOT_TO_CONFIRM, status_REBOOT, status_SHUTDOWN_TO_CONFIRM, status_SHUTDOWN,
            status_STOP_TO_CONFIRM
            ]
        
        return sorted(statusColors)

@total_ordering
class StatusLED():
    status_colors = StatusColor.get_list()
    
    def __init__(self, index, name) -> None:
        self.index = index
        self.name = name
        self.current_status = None
        self.current_status_color = None
        self.current_LEDStatus = None
    
    def __lt__(self, obj):
        if not isinstance(obj, StatusLED):
            raise TypeError("obj must be an instance of StatusLED")
        
        return ((self.index) < (obj.index))
  
    def __gt__(self, obj):
        if not isinstance(obj, StatusLED):
            raise TypeError("obj must be an instance of StatusLED")
        
        return ((self.index) > (obj.index))
  
    def __le__(self, obj):
        if not isinstance(obj, StatusLED):
            raise TypeError("obj must be an instance of StatusLED")
        
        return ((self.index) <= (obj.index))
  
    def __ge__(self, obj):
        if not isinstance(obj, StatusLED):
            raise TypeError("obj must be an instance of StatusLED")
        
        return ((self.index) >= (obj.index))
  
    def __eq__(self, obj):
        if not isinstance(obj, StatusLED):
            raise TypeError("obj must be an instance of StatusLED")
        
        return (self.index == obj.index)
    
    def __str__(self) -> str:
        return f"StatusLED at index {self.index} has name {self.name} and allows these DeviceStatus values: {self.allowed_status}. \
Current status is {self.current_status}, current color is {self.current_status_color} and current LED status is {self.current_LEDStatus}."
    
    def __repr__(self) -> str:
        return f"StatusLED({self.index}, '{self.name}')"
    
    @staticmethod
    def init_list():
        statusLED_RPI = StatusLED(0, LEDnames.RPI)
        statusLED_REBOOT_SHUTDOWN = StatusLED(1, LEDnames.REBOOT_SHUTDOWN)
        statusLED_SENSOR_AUTO = StatusLED(2, LEDnames.SENSOR_AUTO)
        statusLED_SENSOR_MANUAL = StatusLED(3, LEDnames.SENSOR_MANUAL)
        statusLED_SENSOR_ERROR = StatusLED(4, LEDnames.SENSOR_ERROR)
        statusLED_RELAY_AUTO = StatusLED(5, LEDnames.RELAY_AUTO)
        statusLED_RELAY_MANUAL = StatusLED(6, LEDnames.RELAY_MANUAL)
        statusLED_RELAY_ERROR = StatusLED(7, LEDnames.RELAY_ERROR)
        
        statusLEDs = [
            statusLED_RPI, statusLED_REBOOT_SHUTDOWN,
            statusLED_SENSOR_AUTO, statusLED_SENSOR_MANUAL, statusLED_SENSOR_ERROR,
            statusLED_RELAY_AUTO, statusLED_RELAY_MANUAL, statusLED_RELAY_ERROR
            ]
        
        return sorted(statusLEDs)
    
    def set_status(self, status):
        if not isinstance(status, DeviceStatus):
            raise TypeError("status must be an instance of DeviceStatus Enum")
        
        self.current_status = status
        self.current_status_color = find(lambda status_color: status_color.status == status, StatusLED.status_colors)
        self.current_LEDStatus = GeneralStatus.OFF \
            if (self.current_status_color.r == 0 and self.current_status_color.g == 0 and self.current_status_color.b == 0) else GeneralStatus.ON
    
    @staticmethod
    def blink(seq):
        LEDs_to_update = []
        
        for item in seq:
            if isinstance(item, StatusLED) and isinstance(item.current_status_color, StatusColor):
                if item.current_status_color.led_function == LEDFunction.BLINK:
                    item.current_LEDStatus = GeneralStatus(not bool(item.current_LEDStatus.value))
                    LEDs_to_update.append(item)
        
        return sorted(LEDs_to_update)

class SystemStatusItem():
    def __init__(self, name = "", allowed_values = DeviceStatus.NONE, allowed_display_values = DeviceStatus.NONE, current_status = DeviceStatus.NONE,
                 current_status_chain = DeviceStatus.NONE, ts_change = get_formatted_now()) -> None:
        allowed_values = self.check_passed_status_value(allowed_values)
        allowed_display_values = self.check_passed_status_value(allowed_display_values)
        current_status = self.check_passed_status_value(current_status)
        current_status_chain = self.check_passed_status_value(current_status_chain)
        
        if not isinstance(allowed_values, DeviceStatus):
            print(allowed_values)
            raise TypeError("allowed_values must be an instance of DeviceStatus Enum")
        
        if not isinstance(allowed_display_values, DeviceStatus):
            print(allowed_display_values)
            raise TypeError("allowed_display_values must be an instance of DeviceStatus Enum")
        
        if not isinstance(current_status, DeviceStatus):
            print(current_status)
            raise TypeError("current_status must be an instance of DeviceStatus Enum")
        
        if not isinstance(current_status_chain, DeviceStatus):
            print(current_status_chain)
            raise TypeError("current_status_chain must be an instance of DeviceStatus Enum")
                
        if not set(allowed_display_values).issubset(set(allowed_values)):
            raise ValueError(f"Not all allowed_display_values ({allowed_display_values}) appear in allowed_values ({allowed_values}).")
        
        if current_status != DeviceStatus.NONE and current_status not in allowed_values:
            raise ValueError(f"current_value {current_status} is not allowed. Allowed values are : {allowed_values}.")
        
        self.name = name
        self.allowed_values = allowed_values
        self.allowed_display_values = allowed_display_values
        self.current_status = current_status
        self.current_status_chain = current_status_chain
        self.ts_change = ts_change
    
    def __str__(self) -> str:
        return f"SystemStatusItem has name {self.name}, allows the following DeviceStatus values: {self.allowed_values} and allows these DeviceStatus \
values for LEDs: {self.allowed_display_values}. The current DeviceStatus is {self.current_status} and was set at {self.ts_change}."
    
    def __repr__(self) -> str:
        return f"SystemStatusItem('{self.name}', {self.allowed_values}, {self.allowed_display_values}, {self.current_status}, {self.ts_change})"
    
    def check_passed_status_value(self, value):
        if isinstance(value, str):
            values = value.split("|")
            x = DeviceStatus.INVALID
            for i in values:
                x += DeviceStatus[i]
            return DeviceStatus(x)
        else:
            return value
    
    def change_status(self, status, reset_to_last_acknowledged_status = False):
        status = self.check_passed_status_value(status)
        
        if not isinstance(status, DeviceStatus):
            raise TypeError("status must be an instance of DeviceStatus Enum")
        
        if status in self.allowed_values:
            self.ts_change = get_formatted_now()
            
            if self.name == LEDnames.RPI:
                self.current_status = status
                self.current_status_chain = status
            elif self.name == LEDnames.REBOOT_SHUTDOWN:
                self.change_status_reboot_shutdown_helper(status, reset_to_last_acknowledged_status)
            elif self.is_auto_item():
                self.change_status_auto_item_helper(status, reset_to_last_acknowledged_status)
            elif self.is_manual_item():
                self.change_status_manual_item_helper(status, reset_to_last_acknowledged_status)
            elif self.is_error_item():
                pass
        else:
            raise ValueError(f"DeviceStatus {status} is not an allowed status value for {self.name}. Allowed values are: {self.allowed_values}.")
    
    def is_auto_item(self):
        return self.name.endswith("_AUTO")
    
    def is_manual_item(self):
        return self.name.endswith("_MANUAL")
    
    def is_error_item(self):
        return self.name.endswith("_ERROR")
    
    def change_status_reboot_shutdown_helper(self, status, reset_to_last_acknowledged_status):
        if status == status & DeviceStatus.get_acknowledged_status():
            match status:
                case DeviceStatus.NONE | DeviceStatus.REBOOT | DeviceStatus.SHUTDOWN:
                    self.current_status = status
                    self.current_status_chain = status
        elif status == status & DeviceStatus.get_status_for_reset():
            if reset_to_last_acknowledged_status:
                match status:
                    case DeviceStatus.CANCELED:
                        self.current_status = DeviceStatus.NONE
                        self.current_status_chain = DeviceStatus.NONE
            else:
                self.current_status = status
                self.current_status_chain |= status
        elif status == status & DeviceStatus.get_status_requiring_confirmation():
            match status:
                case DeviceStatus.REBOOT_TO_CONFIRM | DeviceStatus.SHUTDOWN_TO_CONFIRM:
                    self.current_status = status
                    self.current_status_chain |= status
    
    def change_status_auto_item_helper(self, status, reset_to_last_acknowledged_status):
        if status == status & DeviceStatus.get_acknowledged_status():
            match status:
                case DeviceStatus.NONE | DeviceStatus.ENABLED | DeviceStatus.WORKING | DeviceStatus.DISABLED:
                    self.current_status = status
                    self.current_status_chain = status
        elif status == status & DeviceStatus.get_status_for_reset():
            if reset_to_last_acknowledged_status:
                match status:
                    case DeviceStatus.CANCELED:
                        if DeviceStatus.ENABLE_TO_CONFIRM == self.current_status_chain & DeviceStatus.ENABLE_TO_CONFIRM:
                            self.current_status = DeviceStatus.DISABLED
                            self.current_status_chain = DeviceStatus.DISABLED
                        elif DeviceStatus.DISABLE_TO_CONFIRM == self.current_status_chain & DeviceStatus.DISABLE_TO_CONFIRM:
                            self.current_status = DeviceStatus.ENABLED
                            self.current_status_chain = DeviceStatus.ENABLED
                    case DeviceStatus.STOP_WORKING:
                        self.current_status = DeviceStatus.ENABLED
                        self.current_status_chain = DeviceStatus.ENABLED
            else:
                self.current_status = status
                self.current_status_chain |= status
        elif status == status & DeviceStatus.get_status_requiring_confirmation():
            match status:
                case DeviceStatus.ENABLE_TO_CONFIRM | DeviceStatus.DISABLE_TO_CONFIRM:
                    self.current_status = status
                    self.current_status_chain |= status
    
    def change_status_manual_item_helper(self, status, reset_to_last_acknowledged_status):
        if status == status & DeviceStatus.get_acknowledged_status():
            match status:
                case DeviceStatus.NONE | DeviceStatus.WORKING:
                    self.current_status = status
                    self.current_status_chain = status
        elif status == status & DeviceStatus.get_status_for_reset():
            if reset_to_last_acknowledged_status:
                match status:
                    case DeviceStatus.CANCELED:
                        if DeviceStatus.MANUAL_TO_CONFIRM == self.current_status_chain & DeviceStatus.MANUAL_TO_CONFIRM:
                            self.current_status = DeviceStatus.NONE
                            self.current_status_chain = DeviceStatus.NONE
                        elif DeviceStatus.STOP_TO_CONFIRM == self.current_status_chain & DeviceStatus.STOP_TO_CONFIRM:
                            self.current_status = DeviceStatus.WORKING
                            self.current_status_chain = DeviceStatus.WORKING
                    case DeviceStatus.STOP_WORKING:
                        self.current_status = DeviceStatus.NONE
                        self.current_status_chain = DeviceStatus.NONE
            else:
                self.current_status = status
                self.current_status_chain |= status
        elif status == status & DeviceStatus.get_status_requiring_confirmation():
            match status:
                case DeviceStatus.MANUAL_TO_CONFIRM | DeviceStatus.STOP_TO_CONFIRM:
                    self.current_status = status
                    self.current_status_chain |= status

    def save_to_db(self) -> None:
        with closing(db.SQLite3DB()) as database:
            database.execute("UPDATE SystemStatus SET TS_Change = ?, Value = ? WHERE Name = ?", (self.ts_change, self.current_status.name, self.name))

class SystemStatusItemEncoder(GenericJSONEncoder):
    _class = SystemStatusItem

class SystemStatusItemDecoder(GenericJSONDecoder):
    _class = SystemStatusItem

class SystemStatus():
    PUMP_START_DEPTH = 15.0
    PUMP_STOP_DEPTH = 6.0
    
    def __init__(self) -> None:
        auto_allowed_values = DeviceStatus.NONE | DeviceStatus.ENABLED | DeviceStatus.WORKING | DeviceStatus.DISABLE_TO_CONFIRM | DeviceStatus.DISABLED | DeviceStatus.ENABLE_TO_CONFIRM | DeviceStatus.CANCELED | DeviceStatus.STOP_WORKING
        auto_allowed_display_values = DeviceStatus.ENABLED | DeviceStatus.WORKING | DeviceStatus.DISABLE_TO_CONFIRM | DeviceStatus.DISABLED | DeviceStatus.ENABLE_TO_CONFIRM
        manual_allowed_values = DeviceStatus.NONE | DeviceStatus.WORKING | DeviceStatus.MANUAL_TO_CONFIRM | DeviceStatus.CANCELED | DeviceStatus.STOP_WORKING | DeviceStatus.STOP_TO_CONFIRM
        manual_allowed_display_values = DeviceStatus.NONE | DeviceStatus.WORKING | DeviceStatus.MANUAL_TO_CONFIRM | DeviceStatus.STOP_TO_CONFIRM
        error_allowed_values = DeviceStatus.NONE | DeviceStatus.ERROR | DeviceStatus.RESET_ERROR
        error_allowed_display_values = DeviceStatus.NONE | DeviceStatus.ERROR
        
        self.rpi = SystemStatusItem(LEDnames.RPI,
                                    DeviceStatus.NONE | DeviceStatus.POWERED_AND_ONLINE | DeviceStatus.POWERED_NO_NETWORK | DeviceStatus.ERROR | DeviceStatus.RESET_ERROR,
                                    DeviceStatus.POWERED_AND_ONLINE | DeviceStatus.POWERED_NO_NETWORK | DeviceStatus.ERROR)
        self.reboot_shutdown = SystemStatusItem(LEDnames.REBOOT_SHUTDOWN,
                                                DeviceStatus.NONE | DeviceStatus.CANCELED | DeviceStatus.REBOOT_TO_CONFIRM | DeviceStatus.REBOOT | DeviceStatus.SHUTDOWN_TO_CONFIRM | DeviceStatus.SHUTDOWN,
                                                DeviceStatus.NONE | DeviceStatus.REBOOT_TO_CONFIRM | DeviceStatus.REBOOT | DeviceStatus.SHUTDOWN_TO_CONFIRM | DeviceStatus.SHUTDOWN)
        self.sensor_auto = SystemStatusItem(LEDnames.SENSOR_AUTO,
                                            auto_allowed_values,
                                            auto_allowed_display_values)
        self.sensor_manual = SystemStatusItem(LEDnames.SENSOR_MANUAL,
                                              manual_allowed_values,
                                              manual_allowed_display_values)
        self.sensor_error = SystemStatusItem(LEDnames.SENSOR_ERROR,
                                             error_allowed_values,
                                             error_allowed_display_values)
        self.relay_auto = SystemStatusItem(LEDnames.RELAY_AUTO,
                                           auto_allowed_values,
                                           auto_allowed_display_values)
        self.relay_manual = SystemStatusItem(LEDnames.RELAY_MANUAL,
                                             manual_allowed_values,
                                             manual_allowed_display_values)
        self.relay_error = SystemStatusItem(LEDnames.RELAY_ERROR,
                                            error_allowed_values,
                                            error_allowed_display_values)
    
    def retrieve_all_from_db(self):
        with closing(db.SQLite3DB()) as database:
            database.execute("SELECT SystemStatusID, Name, Value FROM SystemStatus ORDER BY SystemStatusID")
            return database.cursor.fetchall()
    
    def load_from_db(self):
        rows = self.retrieve_all_from_db()
        for row in rows:
            match row[1]:
                case LEDnames.RPI:
                    self.rpi.change_status(DeviceStatus[row[2]])
                case LEDnames.REBOOT_SHUTDOWN:
                    self.reboot_shutdown.change_status(DeviceStatus[row[2]])
                case LEDnames.SENSOR_AUTO:
                    self.sensor_auto.change_status(DeviceStatus[row[2]])
                case LEDnames.SENSOR_MANUAL:
                    self.sensor_manual.change_status(DeviceStatus[row[2]])
                case LEDnames.SENSOR_ERROR:
                    self.sensor_error.change_status(DeviceStatus[row[2]])
                case LEDnames.RELAY_AUTO:
                    self.relay_auto.change_status(DeviceStatus[row[2]])
                case LEDnames.RELAY_MANUAL:
                    self.relay_manual.change_status(DeviceStatus[row[2]])
                case LEDnames.RELAY_ERROR:
                    self.relay_error.change_status(DeviceStatus[row[2]])
    
    def set_all(self, status):
        self.rpi.change_status(status)
        self.reboot_shutdown.change_status(status)
        self.sensor_auto.change_status(status)
        self.sensor_manual.change_status(status)
        self.sensor_error.change_status(status)
        self.relay_auto.change_status(status)
        self.relay_manual.change_status(status)
        self.relay_error.change_status(status)
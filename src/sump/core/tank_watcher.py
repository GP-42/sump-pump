#! /usr/bin/python3

#hcsr04_sensor
from core.hcsr04_sensor import Hcsr04Sensor
#A02YYUW_sensor
#from core.A02YYUW_sensor import DFRobot_A02_Distance
from core.measurement import Measurement
from utilities.configuration.toml.toml_configuration import TomlConfiguration

#A02YYUW_sensor
#import time
import RPi.GPIO as gpio
import statistics

class TankWatcher:
    @staticmethod
    def log_water_depth(sensor, sensor_height, automatic) -> Measurement:
            """
            Read sensor multiple times to get a stable reading (calculate mean) and log to the logger store.
            Readings are taken 20 times. Outliers > median +/- 1 std dev are discarded.
            Arithmetic mean of the remaining samples is calculated to 2 decimal places.

            :param sensor: the sensor to read
            :param sensor_height: height of the sensor above the tank
            """

            num_measures = 20
            samples = []
            for i in range(0, num_measures):
                #hcsr04_sensor
                samples.append(sensor.distance())
                #A02YYUW_sensor
                #samples.append(sensor.getDistance()/10)
                #time.sleep(0.3)
                print("Measured Distance = %f cm" % samples[i])

            # remove outliers
            stdev = statistics.stdev(samples)
            print("-- stdev = %f" % stdev)
            median = statistics.median(samples)
            print("-- median = %f" % median)
            clean_data = [x for x in samples if x > median - 1 * stdev]
            clean_data = [x for x in clean_data if x < median + 1 * stdev]
            print("-- len samples = %d; len clean_data = %d" % (len(samples), len(clean_data)))

            #additional code for A02YYUW_sensor
            # if len(clean_data) == 0:
            #      clean_data=[median]
            
            # calculate mean measurement
            with_outliers = statistics.mean(samples)
            print("Avg. measurement (incl. outliers) = %.2f cm" % with_outliers)
            clean_measure = statistics.mean(clean_data)
            print("Avg. measurement (excl. outliers) = %.2f cm" % clean_measure)
            water_depth = round(sensor_height - clean_measure, 2)  # log to 2 decimal places

            if water_depth >= 0:
                print("Logging water depth = %s cm" % water_depth)
            else:
                print("Skipping -ve water depth (%s cm)" % water_depth)
            
            return Measurement("", sensor_height, samples, stdev, median, clean_data, with_outliers, clean_measure, water_depth, automatic)
        
    @staticmethod
    def measure(automatic = False) -> Measurement:
        try:
            config = TomlConfiguration()
            hcsr04_sensor = Hcsr04Sensor(config.Hcsr04Sensor.gpio_mode, config.Hcsr04Sensor.gpio_trigger_pin, config.Hcsr04Sensor.gpio_echo_pin)
            result = TankWatcher.log_water_depth(hcsr04_sensor, config.TankWatcher.sensor_height, automatic)

            # A02YYUW_sensor = DFRobot_A02_Distance()
            # A02YYUW_sensor.set_dis_range(0,4500)
            # result = TankWatcher.log_water_depth(A02YYUW_sensor, TankWatcher.SENSOR_HEIGHT, automatic)
            
            return result

        except KeyboardInterrupt:
            print("Measurement stopped by User")
        
        finally:
            gpio.cleanup()
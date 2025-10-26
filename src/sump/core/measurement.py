#! /usr/bin/python3

from contextlib import closing
from utilities.formatters import get_formatted_now
from utilities.generics import GenericJSONEncoder, GenericJSONDecoder

import utilities.sqlite3db as db

class Measurement:
    def __init__(self, ts_measure = "", sensor_height = 0.0, readings = [], stdev = 0.000000, median = 0.000000, clean_data = [], with_outliers = 0.00, 
                 clean_measure = 0.00, water_depth = 0.00, automatic = False) -> None:
        self.ts_measure = get_formatted_now() if ts_measure == "" else ts_measure
        self.sensor_height = sensor_height
        self.readings = readings
        self.stdev = stdev
        self.median = median
        self.clean_data = clean_data
        self.with_outliers = with_outliers
        self.clean_measure = clean_measure
        self.water_depth = water_depth
        self.automatic = automatic
    
    def __str__(self) -> str:
        return f"Waterdepth : {self.water_depth}"
    
    def __repr__(self) -> str:
        return f"Measurement({self.ts_measure}, {self.sensor_height}, {self.readings}, {self.stdev}, {self.median}, {self.clean_data}, \
{self.with_outliers}, {self.clean_measure}, {self.water_depth}, {self.automatic})"
    
    def save_to_db(self) -> None:
        with closing(db.SQLite3DB()) as database:
            new_id = database.execute("INSERT INTO Measurement(TS_Measure, SensorHeight, StDev, Median, WithOutliers, CleanMeasure, WaterDepth, Automatic) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", 
                                      (self.ts_measure, self.sensor_height, self.stdev, self.median, self.with_outliers, self.clean_measure, self.water_depth, int(self.automatic)))

            for i in self.readings:
                is_clean_data = (1 if (i in self.clean_data) else 0)
                database.execute("INSERT INTO Sample(MeasurementID, Data, IsCleanData) VALUES(?, ?, ?)", (new_id, i, is_clean_data))

class MeasurementEncoder(GenericJSONEncoder):
    _class = Measurement

class MeasurementDecoder(GenericJSONDecoder):
    _class = Measurement
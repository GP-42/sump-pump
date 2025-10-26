CREATE TABLE IF NOT EXISTS "Measurement" (
	"MeasurementID"	INTEGER NOT NULL UNIQUE,
	"TS_InsertDB"	TEXT NOT NULL DEFAULT (datetime('now','localtime')),
	"TS_Measure"	TEXT NOT NULL,
	"SensorHeight"	REAL NOT NULL,
	"StDev"	REAL NOT NULL,
	"Median"	REAL NOT NULL,
	"WithOutliers"	REAL NOT NULL,
	"CleanMeasure"	REAL NOT NULL,
	"WaterDepth"	REAL NOT NULL,
	"Automatic"	INTEGER NOT NULL,
	PRIMARY KEY("MeasurementID" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "Sample" (
	"SampleID"	INTEGER NOT NULL UNIQUE,
	"MeasurementID"	INTEGER NOT NULL,
	"Data"	REAL NOT NULL,
	"IsCleanData"	INTEGER NOT NULL,
	PRIMARY KEY("SampleID" AUTOINCREMENT),
	FOREIGN KEY("MeasurementID") REFERENCES "Measurement"("MeasurementID")
);

CREATE TABLE IF NOT EXISTS "SystemStatus" (
	"SystemStatusID"	INTEGER NOT NULL UNIQUE,
	"TS_UpdateDB"	TEXT NOT NULL DEFAULT (datetime('now','localtime')),
	"TS_Change"	TEXT NOT NULL,
	"Name"	TEXT NOT NULL UNIQUE,
	"Value"	TEXT NOT NULL,
	PRIMARY KEY("SystemStatusID" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "SystemStatusHistory" (
	"SystemStatusID"	INTEGER NOT NULL,
	"TS_UpdateDB"	TEXT NOT NULL,
	"TS_Change"	TEXT NOT NULL,
	"Name"	TEXT NOT NULL,
	"Value"	TEXT NOT NULL,
	UNIQUE("SystemStatusID","TS_UpdateDB","TS_Change","Name","Value"),
	FOREIGN KEY("SystemStatusID") REFERENCES "SystemStatus"("SystemStatusID")
);

CREATE TRIGGER IF NOT EXISTS trg_log_system_status_insert
	AFTER INSERT
	ON SystemStatus
BEGIN
	INSERT INTO SystemStatusHistory(SystemStatusID, TS_UpdateDB, TS_Change, Name, Value)
	SELECT SystemStatusID, TS_UpdateDB, TS_Change, Name, Value
	FROM SystemStatus
	WHERE Name = new.Name;
END;

CREATE TRIGGER IF NOT EXISTS trg_log_system_status_update
	AFTER UPDATE
	ON SystemStatus
	WHEN new.TS_UpdateDB = old.TS_UpdateDB
BEGIN
	UPDATE SystemStatus
	SET TS_UpdateDB = datetime('now','localtime')
	WHERE SystemStatusID = old.SystemStatusID;
	
	INSERT INTO SystemStatusHistory(SystemStatusID, TS_UpdateDB, TS_Change, Name, Value)
	SELECT SystemStatusID, TS_UpdateDB, TS_Change, Name, Value
	FROM SystemStatus
	WHERE Name = new.Name;
END;

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'RPI', 'POWERED_AND_ONLINE');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'REBOOT_SHUTDOWN', 'NONE');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'SENSOR_AUTO', 'ENABLED');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'SENSOR_MANUAL', 'NONE');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'SENSOR_ERROR', 'NONE');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'RELAY_AUTO', 'ENABLED');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'RELAY_MANUAL', 'NONE');

INSERT INTO SystemStatus(TS_UpdateDB, TS_Change, Name, Value)
VALUES('2024-01-01 00:00:00', '2024-01-01 00:00:00.000000', 'RELAY_ERROR', 'NONE');
# mux_helper.py
"""
@file mux_helper.py
@brief Stellt Funktionen zum Umschalten des TCA9548A-Multiplexers bereit sowie eine Lock-Mechanik für I2C.
"""

import fcntl
import smbus
import time
import os

LOCKFILE_PATH = "/tmp/mux_i2c.lock"
MUX_ADDRESS   = 0x70
I2C_BUS       = 1

SENSOR_CHANNEL_MAP = {
    "SDP810": 2,
    "MCP9600_ENV": 0,
    "MCP9600_AIRFLOW": 1,
    "BME280": 0
}

def acquire_i2c_lock():
    """
    @fn acquire_i2c_lock()
    @brief Erstellt/öffnet eine Lock-Datei und belegt einen exklusiven Lock.
    @return Dateiobjekt, das den Lock repräsentiert
    """
    lockfile = open(LOCKFILE_PATH, "w")
    fcntl.flock(lockfile, fcntl.LOCK_EX)
    return lockfile

def release_i2c_lock(lockfile):
    """
    @fn release_i2c_lock(lockfile)
    @brief Gibt den Lock frei und schließt das Dateiobjekt.
    @param lockfile: Dateiobjekt, das von acquire_i2c_lock() zurückgegeben wurde
    """
    fcntl.flock(lockfile, fcntl.LOCK_UN)
    lockfile.close()

def switch_mux_channel_for(sensor_name: str):
    """
    @fn switch_mux_channel_for(sensor_name: str)
    @brief Aktiviert den Multiplexer-Kanal, der in SENSOR_CHANNEL_MAP hinterlegt ist.
    @param sensor_name: Name des Sensors, z.B. "SDP810" oder "BME280"
    """
    channel = SENSOR_CHANNEL_MAP.get(sensor_name)
    if channel is None:
        raise ValueError(f"Sensor '{sensor_name}' nicht im Mapping definiert.")

    bus = smbus.SMBus(I2C_BUS)
    bus.write_byte(MUX_ADDRESS, 1 << channel)
    time.sleep(0.05)
    bus.close()

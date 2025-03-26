# MCP9600_Airflow.py
"""
@file MCP9600_Airflow.py
@brief Liest Ambient- und Thermocouple-Temperatur vom MCP9600 und schätzt daraus eine Luftströmung.
       Nutzt mux_helper für den Multiplexer und eine Lock-Mechanik.
"""

import smbus2
import time
import math
from mux_helper import acquire_i2c_lock, release_i2c_lock, switch_mux_channel_for

I2C_ADDRESS                = 0x67
AMBIENT_TEMP_REGISTER      = 0x00
THERMOCOUPLE_TEMP_REGISTER = 0x01

CALIBRATION_C = 2.5
TEMP_OFFSET   = 0.2

def main():
    """
    @fn main()
    @brief Schaltet auf den MCP9600_AIRFLOW-Kanal, liest die Temperaturen aus und berechnet eine Strömungsgeschwindigkeit.
    """
    lockfile = acquire_i2c_lock()
    try:
        switch_mux_channel_for("MCP9600_AIRFLOW")

        bus = smbus2.SMBus(1)
        try:
            ambient_temp      = read_temp(bus, AMBIENT_TEMP_REGISTER)
            thermocouple_temp = read_temp(bus, THERMOCOUPLE_TEMP_REGISTER)
        finally:
            bus.close()

        if (ambient_temp is None) or (thermocouple_temp is None):
            return

        delta_temp = thermocouple_temp - ambient_temp
        print(f"Ambient: {ambient_temp:.2f} °C, "
              f"Thermocouple: {thermocouple_temp:.2f} °C, "
              f"Delta: {delta_temp:.2f} °C")

        if delta_temp <= TEMP_OFFSET:
            wind_speed = 0.0
        else:
            effective_delta = delta_temp - TEMP_OFFSET
            wind_speed = CALIBRATION_C * math.sqrt(effective_delta)

        print(f"{wind_speed:.2f}")

    finally:
        release_i2c_lock(lockfile)

def read_temp(bus, register):
    """
    @fn read_temp(bus, register)
    @brief Liest ein MCP9600-Register (Ambient oder Thermocouple) und wandelt es in °C um.
    @param bus: smbus2.SMBus Objekt
    @param register: Zielregister (z.B. 0x00 für Ambient, 0x01 für Thermocouple)
    @return Temperatur als float oder None
    """
    try:
        data = bus.read_i2c_block_data(I2C_ADDRESS, register, 2)
        raw = (data[0] << 8) | data[1]
        if raw & (1 << 15):
            raw -= (1 << 16)
        return raw / 16.0
    except Exception as e:
        print(f"Fehler beim Lesen von Register 0x{register:02X}: {e}")
        return None

if __name__ == "__main__":
    main()

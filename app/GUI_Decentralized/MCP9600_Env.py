# MCP9600_Env.py
"""
@file MCP9600_Env.py
@brief Liest die Umgebungstemperatur (Ambient) vom MCP9600 aus (Register 0x00).
       Nutzt mux_helper zum Umschalten des Multiplexers.
"""

import smbus2
import time
from mux_helper import acquire_i2c_lock, release_i2c_lock, switch_mux_channel_for

I2C_ADDRESS           = 0x67
AMBIENT_TEMP_REGISTER = 0x00

def read_ambient_temperature():
    """
    @fn read_ambient_temperature()
    @brief Liest die Ambient-Temperatur in °C vom MCP9600.
    @return float oder None
    """
    lockfile = acquire_i2c_lock()
    try:
        switch_mux_channel_for("MCP9600_ENV")

        bus = smbus2.SMBus(1)
        try:
            data = bus.read_i2c_block_data(I2C_ADDRESS, AMBIENT_TEMP_REGISTER, 2)
            raw_temp = (data[0] << 8) | data[1]
            if raw_temp & (1 << 15):
                raw_temp -= (1 << 16)
            return raw_temp / 16.0
        finally:
            bus.close()
    finally:
        release_i2c_lock(lockfile)

def main():
    """
    @fn main()
    @brief Ruft read_ambient_temperature() auf und gibt das Ergebnis aus.
    """
    temp = read_ambient_temperature()
    if temp is not None:
        print(f"{temp:.2f}")

if __name__ == "__main__":
    main()

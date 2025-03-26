# sdp810_reader.py
"""
@file sdp810_reader.py
@brief Liest den SDP810-Sensor lokal über I2C aus und verwendet mux_helper zur Multiplexer-Umschaltung.
"""

import sys
import time
import smbus
from mux_helper import acquire_i2c_lock, release_i2c_lock, switch_mux_channel_for

SDP810_ADDRESS = 0x25

def read_sdp810(measure_type='pressure'):
    """
    @fn read_sdp810(measure_type='pressure')
    @brief Liest den SDP810-Sensorwert vom lokalen I2C-Bus.
    @param measure_type: 'pressure' oder 'temperature'
    @return Float-Wert oder None bei Fehler
    """
    lockfile = acquire_i2c_lock()
    try:
        switch_mux_channel_for("SDP810")
        bus = smbus.SMBus(1)

        bus.write_i2c_block_data(SDP810_ADDRESS, 0x3F, [0xF9])
        time.sleep(0.8)

        if measure_type == 'pressure':
            bus.write_i2c_block_data(SDP810_ADDRESS, 0x36, [0x15])
        else:
            bus.write_i2c_block_data(SDP810_ADDRESS, 0x36, [0x1E])

        time.sleep(0.5)
        reading = bus.read_i2c_block_data(SDP810_ADDRESS, 0, 9)
        bus.close()

        if measure_type == 'pressure':
            val = reading[0] + float(reading[1]) / 255
            if 0 <= val < 128:
                return val * 240 / 256
            elif 128 < val <= 256:
                return -(256 - val) * 240 / 256
            elif val == 128:
                return 99999999
        else:
            val = reading[3] + float(reading[4]) / 255
            if 0 <= val <= 100:
                return val * 255 / 200
            elif 200 <= val <= 256:
                return -(256 - val) * 255 / 200
    finally:
        release_i2c_lock(lockfile)
    return None

def main():
    """
    @fn main()
    @brief Ruft read_sdp810 auf und gibt den Wert (falls vorhanden) auf stdout aus.
    """
    measure_type = sys.argv[1] if len(sys.argv) > 1 else 'pressure'
    value = read_sdp810(measure_type)
    if value is not None:
        print(f"{value:.2f}")

if __name__ == "__main__":
    main()

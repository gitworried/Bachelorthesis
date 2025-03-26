# aggregator.py
"""
@file aggregator.py
@brief Aggregiert Messwerte verschiedener Sensoren über den TCA9548A-Multiplexer und gibt sie als JSON aus.
"""

import smbus2
import time
import json
import sys

MUX_ADDRESS       = 0x70
CHANNEL_0_BITMASK = 0x01
CHANNEL_1_BITMASK = 0x02
CHANNEL_2_BITMASK = 0x04

def select_channel(bus, channel_mask):
    """
    @fn select_channel(bus, channel_mask)
    @brief Aktiviert bestimmte Kanäle am Multiplexer.
    @param bus: smbus2.SMBus Objekt
    @param channel_mask: Bitmaske (z.B. 0x01 für Kanal 0)
    """
    bus.write_byte_data(MUX_ADDRESS, 0x00, channel_mask)
    time.sleep(0.01)

BME280_ADDR = 0x77
def read_bme280(bus):
    """
    @fn read_bme280(bus)
    @brief Beispielhaftes Auslesen eines BME280 (liest hier nur die Chip-ID und verwendet Platzhalterwerte).
    @param bus: smbus2.SMBus Objekt
    @return dict mit Beispielwerten und Chip-ID
    """
    chip_id = bus.read_byte_data(BME280_ADDR, 0xD0)
    temperature = 25.0
    humidity    = 45.0
    pressure    = 1000.0
    return {
        "bme_temp": temperature,
        "bme_hum":  humidity,
        "bme_pres": pressure,
        "bme_chip": chip_id
    }

MCP9600_ADDR = 0x67
def read_mcp9600(bus):
    """
    @fn read_mcp9600(bus)
    @brief Liest ein Registerpaar für die Ambient-Temperatur des MCP9600.
    @param bus: smbus2.SMBus Objekt
    @return dict mit Key 'mcp_temp'
    """
    data = bus.read_i2c_block_data(MCP9600_ADDR, 0x00, 2)
    raw_temp = (data[0] << 8) | data[1]
    temperature = raw_temp / 16.0
    return {"mcp_temp": temperature}

SDP810_ADDR = 0x25
def read_sdp810(bus):
    """
    @fn read_sdp810(bus)
    @brief Minimales Beispiel zum Auslesen des SDP810 (2 Bytes + Umrechnung).
    @param bus: smbus2.SMBus Objekt
    @return dict mit Key 'sdp_pressure'
    """
    data = bus.read_i2c_block_data(SDP810_ADDR, 0, 2)
    raw_val = (data[0] << 8) | data[1]
    pressure_pa = raw_val * 2.0
    return {"sdp_pressure": pressure_pa}

def main():
    """
    @fn main()
    @brief Liest nacheinander BME280, MCP9600 und SDP810 aus, fasst die Werte in einem JSON-Objekt zusammen.
    """
    bus = smbus2.SMBus(1)
    try:
        result = {}

        select_channel(bus, CHANNEL_0_BITMASK)
        result.update(read_bme280(bus))

        select_channel(bus, CHANNEL_1_BITMASK)
        result.update(read_mcp9600(bus))

        select_channel(bus, CHANNEL_2_BITMASK)
        result.update(read_sdp810(bus))

        print(json.dumps(result))

    except Exception as e:
        print(f"Aggregator error: {e}", file=sys.stderr)
    finally:
        bus.close()

if __name__ == "__main__":
    main()

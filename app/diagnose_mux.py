# diagnose_mux.py
"""
@file diagnose_mux.py
@brief Führt Diagnosen am TCA9548A-Multiplexer durch, indem kanalweise umgeschaltet und gescannt wird.
"""

import smbus
import time

def scan_by_read_byte(bus, start=0x03, end=0x78):
    """
    @fn scan_by_read_byte(bus, start=0x03, end=0x78)
    @brief Spricht Geräte in [start, end) per read_byte an.
    @param bus: smbus-SMBus Objekt
    @param start: Startadresse
    @param end: Endadresse (exklusiv)
    @return Liste gefundener I2C-Adressen
    """
    found = []
    for addr in range(start, end):
        try:
            bus.read_byte(addr)
            found.append(addr)
        except OSError:
            pass
    return found

def scan_by_write_quick(bus, start=0x03, end=0x78):
    """
    @fn scan_by_write_quick(bus, start=0x03, end=0x78)
    @brief Spricht Geräte in [start, end) per write_quick an.
    @param bus: smbus-SMBus Objekt
    @param start: Startadresse
    @param end: Endadresse (exklusiv)
    @return Liste gefundener I2C-Adressen
    """
    found = []
    for addr in range(start, end):
        try:
            bus.write_quick(addr)
            found.append(addr)
        except OSError:
            pass
    return found

def main():
    """
    @fn main()
    @brief Wechselt kanalweise durch den Multiplexer und führt Scans durch.
    """
    I2C_BUS      = 1
    MUX_ADDR     = 0x70
    SKIP_CHANNEL = 4
    bus = smbus.SMBus(I2C_BUS)

    print("=== Multiplexer-Diagnose ===")    
    
    # Test: Ist der Multiplexer erreichbar?
    try:
        bus.read_byte(MUX_ADDR)
        print(f"MUX 0x{MUX_ADDR:02X} ist erreichbar.\n")
    except OSError as e:
        print(f"Fehler: MUX 0x{MUX_ADDR:02X} nicht erreichbar ({e}). Abbruch.")
        return

    # Kanalweise Diagnose
    for channel in range(8):
        if channel == SKIP_CHANNEL:
            print(f"--- Kanal {channel} wird übersprungen. ---\n")
            continue

        print(f"--- Umschalten auf Kanal {channel} ---")
        try:
            bus.write_byte(MUX_ADDR, 1 << channel)
            time.sleep(0.1)
        except OSError as e:
            print(f"   Fehler beim Umschalten auf Kanal {channel}: {e}")
            continue

        # Control-Register lesen
        try:
            ctrl_val = bus.read_byte(MUX_ADDR)
            print(f"   Control-Register: 0x{ctrl_val:02X} (binär: {ctrl_val:08b})")
        except OSError as e:
            print(f"   Konnte Control-Register nicht lesen: {e}")

        # Scan per read_byte()
        print("   -> scan_by_read_byte:")
        found_read = scan_by_read_byte(bus)
        if found_read:
            print(f"      Gefundene Adressen: {[f'0x{a:02X}' for a in found_read]}")
        else:
            print("      Keine Adressen gefunden.")

        # Scan per write_quick()
        print("   -> scan_by_write_quick:")
        found_quick = scan_by_write_quick(bus)
        if found_quick:
            print(f"      Gefundene Adressen: {[f'0x{a:02X}' for a in found_quick]}")
        else:
            print("      Keine Adressen gefunden.")

        print("")

if __name__ == "__main__":
    main()

# step_channel.py
"""
@file step_channel.py
@brief Schaltet den TCA9548A-Multiplexer kanalweise durch und führt einen I2C-Scan durch.
"""

import smbus
import time

def scan_i2c_addresses(bus, start=0x03, end=0x78):
    """
    @fn scan_i2c_addresses(bus, start=0x03, end=0x78)
    @brief Scannt I2C-Adressen im Bereich [start, end).
    @param bus: smbus-SMBus Objekt
    @param start: Startadresse (Default: 0x03)
    @param end: Endadresse (Default: 0x78, exklusive Grenze)
    @return Liste gefundener I2C-Adressen als int-Werte
    """
    found = []
    for addr in range(start, end):
        try:
            bus.read_byte(addr)
            found.append(addr)
        except OSError:
            pass
    return found

def main():
    """
    @fn main()
    @brief Führt den schrittweisen Kanaltest am TCA9548A-Multiplexer durch.
    """
    I2C_BUS = 1
    MUX_ADDR = 0x70
    SKIP_CHANNEL = 4
    CHANNELS = [ch for ch in range(8) if ch != SKIP_CHANNEL]

    bus = smbus.SMBus(I2C_BUS)

    print("=== TCA9548A Step-by-step Kanaltest ===\n")

    # Multiplexer erreichbar?
    try:
        bus.read_byte(MUX_ADDR)
        print(f"Multiplexer 0x{MUX_ADDR:02X} erreichbar.")
    except OSError as e:
        print(f"Fehler: Multiplexer 0x{MUX_ADDR:02X} nicht erreichbar: {e}")
        return

    # Alle Kanäle deaktivieren (Control‐Byte = 0x00)
    print("Setze alle Kanäle auf OFF (Control‐Byte = 0x00).")
    try:
        bus.write_byte(MUX_ADDR, 0x00)
        time.sleep(0.1)
    except OSError as e:
        print(f"Fehler beim Deaktivieren aller Kanäle: {e}")
        return

    # Nacheinander die Kanäle aktivieren
    for channel in CHANNELS:
        print(f"\n--- Nächster Kanal: {channel} ---")
        user_input = input("Drücke ENTER, um diesen Kanal zu AKTIVIEREN (oder 'q' zum Beenden): ")
        if user_input.strip().lower() == 'q':
            print("Beendet.")
            break

        try:
            bus.write_byte(MUX_ADDR, 1 << channel)
            time.sleep(0.1)
        except OSError as e:
            print(f"Fehler beim Aktivieren von Kanal {channel}: {e}")
            continue

        # Control‐Register lesen
        try:
            ctrl_val = bus.read_byte(MUX_ADDR)
            print(f"Control‐Register jetzt: 0x{ctrl_val:02X} (binär: {ctrl_val:08b})")
        except OSError as e:
            print(f"Konnte Control‐Register nicht lesen: {e}")

        print("Scanne jetzt Adressen 0x03..0x77 auf diesem Kanal...")
        found_addrs = scan_i2c_addresses(bus)
        if found_addrs:
            print("Gefundene Adressen:")
            for addr in found_addrs:
                print(f"  - 0x{addr:02X}")
        else:
            print("Keine Geräte gefunden.")

        user_input = input("Drücke ENTER, um den Kanal wieder AUSzuschalten (oder 'q' zum Beenden): ")
        if user_input.strip().lower() == 'q':
            print("Beendet.")
            break

        try:
            bus.write_byte(MUX_ADDR, 0x00)
            time.sleep(0.1)
            print("Alle Kanäle wieder OFF (0x00).")
        except OSError as e:
            print(f"Fehler beim Deaktivieren aller Kanäle nach Kanal {channel}: {e}")

    print("\n=== Test komplett ===")

if __name__ == "__main__":
    main()

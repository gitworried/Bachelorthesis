# sdp810.py
"""
@file sdp810.py
@brief Bietet Zugriff auf den SDP810-Sensor (lokal via mux_helper oder per SSH).
"""

import smbus
import time
import paramiko
import sys
import fcntl
from mux_helper import acquire_i2c_lock, release_i2c_lock, switch_mux_channel_for

SDP810_ADDRESS = 0x25

def read_sdp810_local(measure_type='pressure'):
    """
    @fn read_sdp810_local(measure_type='pressure')
    @brief Liest den SDP810-Sensorwert lokal vom I2C-Bus.
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
        return None
    finally:
        release_i2c_lock(lockfile)

def read_sdp810_ssh(hostname, username, password, measure_type='pressure'):
    """
    @fn read_sdp810_ssh(hostname, username, password, measure_type='pressure')
    @brief Liest den SDP810-Sensor via SSH durch Remote-Ausführung von sdp810_reader.py.
    @param hostname: SSH-Hostname
    @param username: SSH-Benutzername
    @param password: SSH-Passwort
    @param measure_type: 'pressure' oder 'temperature'
    @return Float-Wert oder None
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)

        command = f"python3 /home/Eiffel/GUI/ssh_control/sdp810_reader.py {measure_type}"
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error  = stderr.read().decode().strip()

        if error:
            print(f"SSH Error: {error}")
            return None
        try:
            return float(output)
        except ValueError:
            print(f"Fehler beim Parsen der Ausgabe: {output}")
            return None
    except Exception as e:
        print(f"SSH-Verbindungsfehler: {e}")
        return None

def read_sdp810(is_ssh, hostname=None, username=None, password=None, measure_type='pressure'):
    """
    @fn read_sdp810(is_ssh, hostname=None, username=None, password=None, measure_type='pressure')
    @brief Gemeinsame Zugriffsmethode auf den SDP810 (lokal oder via SSH).
    @param is_ssh: Boolean, True = SSH, False = lokal
    @param hostname: SSH-Hostname
    @param username: SSH-Benutzer
    @param password: SSH-Passwort
    @param measure_type: 'pressure' oder 'temperature'
    @return Float-Wert oder None
    """
    if is_ssh:
        if not (hostname and username and password):
            print("SSH-Anmeldedaten fehlen.")
            return None
        return read_sdp810_ssh(hostname, username, password, measure_type)
    else:
        return read_sdp810_local(measure_type)

def main():
    """
    @fn main()
    @brief Beispielhafter Aufruf von read_sdp810.
    """
    is_ssh = False
    wert = read_sdp810(is_ssh, measure_type='pressure')
    if wert is not None:
        print(f"{wert:.2f}")

if __name__ == "__main__":
    main()

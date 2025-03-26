# heating.py
"""
@file heating.py
@brief Steuert die Heizung via PWM und loggt Daten des BME280-Sensors in /tmp/bme_data.csv.
       Nutzt mux_helper für Multiplexer und Lock-Mechanik.
"""

import time
import os
import pigpio
import board
import busio
import smbus
from adafruit_bme280.advanced import Adafruit_BME280_I2C
from config.settings import (
    HEATER_PIN, FAN_PIN,
    load_settings
)
from mux_helper import acquire_i2c_lock, release_i2c_lock, switch_mux_channel_for

SETPOINT_FILE    = "/tmp/heater_setpoint.txt"
BME_FILE         = "/tmp/bme_data.csv"
BME_SENSOR_NAME  = "BME280"

def read_setpoint():
    """
    @fn read_setpoint()
    @brief Liest die Solltemperatur aus /tmp/heater_setpoint.txt (falls vorhanden).
    @return float oder None
    """
    if not os.path.exists(SETPOINT_FILE):
        return None
    with open(SETPOINT_FILE, "r") as f:
        line = f.read().strip()
        if not line:
            return None
        try:
            return float(line)
        except ValueError:
            return None

def main():
    """
    @fn main()
    @brief Hauptfunktion: Initialisiert pigpio, setzt PWM-Frequenz, liest BME280 aus und regelt die Heizung.
    """
    settings = load_settings()
    pwm_frequency = settings.get("pwm_frequency", 5000)

    pi = pigpio.pi()
    if not pi.connected:
        print("Cannot connect to pigpio daemon!")
        return

    pi.set_PWM_frequency(HEATER_PIN, pwm_frequency)
    pi.set_PWM_frequency(FAN_PIN, pwm_frequency)

    lockfile = acquire_i2c_lock()
    try:
        switch_mux_channel_for(BME_SENSOR_NAME)
        i2c = busio.I2C(board.SCL, board.SDA)

        bme280 = None
        for _ in range(3):
            try:
                bme280 = Adafruit_BME280_I2C(i2c, address=0x76)
                break
            except Exception as e:
                print(f"Fehler bei der BME280-Initialisierung (0x76): {e}")
                time.sleep(1)

        if bme280 is None:
            print("BME280 konnte nicht initialisiert werden.")
            release_i2c_lock(lockfile)
            return
    finally:
        release_i2c_lock(lockfile)

    heater_on = False
    hysteresis = 1.0

    if not os.path.exists(BME_FILE):
        with open(BME_FILE, "w") as f:
            f.write("timestamp,temperature,humidity,pressure\n")

    print("Heizungs-Skript gestartet. Loggt BME280-Daten (~5 Hz). Wenn kein Sollwert vorhanden ist, wird 20°C angenommen (nur Messung).")
    try:
        while True:
            # I2C-Lock holen und BME280 auslesen
            lockfile = acquire_i2c_lock()
            try:
                switch_mux_channel_for(BME_SENSOR_NAME)
                temp = bme280.temperature
                hum  = bme280.humidity
                pres = bme280.pressure
            except Exception as e:
                print(f"Fehler beim Lesen des BME280: {e}")
                temp, hum, pres = None, None, None
            finally:
                release_i2c_lock(lockfile)

            if temp is not None:
                with open(BME_FILE, "a") as f:
                    f.write(f"{time.time()},{temp},{hum},{pres}\n")

            raw_setpoint = read_setpoint()
            if raw_setpoint is None:
                setpoint = 20.0
                control_active = False
            else:
                setpoint = raw_setpoint
                control_active = True

            if control_active and (temp is not None):
                upper = setpoint + hysteresis
                lower = setpoint - hysteresis
                if heater_on and (temp >= upper):
                    pi.set_PWM_dutycycle(HEATER_PIN, 0)
                    heater_on = False
                elif not heater_on and (temp <= lower):
                    pi.set_PWM_dutycycle(HEATER_PIN, 255)
                    heater_on = True
            else:
                if heater_on:
                    pi.set_PWM_dutycycle(HEATER_PIN, 0)
                    heater_on = False

            time.sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        pi.set_PWM_dutycycle(HEATER_PIN, 0)
        pi.set_PWM_dutycycle(FAN_PIN, 0)
        pi.stop()
        print("Heizungs-Skript beendet => Heizung und Lüfter AUS.")

if __name__ == "__main__":
    main()

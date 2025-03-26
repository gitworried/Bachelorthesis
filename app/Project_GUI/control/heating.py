# control/heating.py
"""
@file heating.py
@brief Dieses Skript steuert die Heizung auf Basis einer einfachen Hysterese-Logik. 
       Es liest kontinuierlich Daten vom BME280-Sensor aus und schreibt diese in /tmp/bme_data.csv.
       Wenn ein Sollwert (Setpoint) in /tmp/heater_setpoint.txt liegt, wird die Heizung 
       anhand des Hystereseverhaltens (±1°C) ein- oder ausgeschaltet.
"""

import time
import os
import pigpio
import board
import busio
from adafruit_bme280.advanced import Adafruit_BME280_I2C
from config.settings import (
    HEATER_PIN, FAN_PIN, INVERT_PWM,
    load_settings
)

SETPOINT_DATEI = "/tmp/heater_setpoint.txt"
BME_DATEI = "/tmp/bme_data.csv"

def lese_sollwert():
    """
    @fn lese_sollwert()
    @brief Liest den Sollwert (Temperatur) aus /tmp/heater_setpoint.txt.
    @return float oder None, falls keine Datei oder kein gültiger Wert vorliegt.
    """
    if not os.path.exists(SETPOINT_DATEI):
        return None
    with open(SETPOINT_DATEI, "r") as f:
        inhalt = f.read().strip()
        if not inhalt:
            return None
        try:
            return float(inhalt)
        except ValueError:
            return None

def main():
    """
    @fn main()
    @brief Hauptfunktion: Initialisiert pigpio und BME280, regelt die Heizung und
           protokolliert Messwerte in /tmp/bme_data.csv.
    """
    einstellungen = load_settings()
    pwm_frequency = einstellungen["pwm_frequency"]

    pi = pigpio.pi()
    if not pi.connected:
        print("Konnte keine Verbindung zum pigpio-Daemon herstellen!")
        return

    # PWM-Frequenz für Heizung und Lüfter setzen
    pi.set_PWM_frequency(HEATER_PIN, pwm_frequency)
    pi.set_PWM_frequency(FAN_PIN, pwm_frequency)

    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = None
    versuche = 3

    for _ in range(versuche):
        try:
            bme280 = Adafruit_BME280_I2C(i2c, address=0x76)
            break
        except Exception as e:
            print(f"Fehler bei der Initialisierung des BME280 (0x76): {e}")
            time.sleep(1)

    if bme280 is None:
        print("BME280 konnte nach mehreren Versuchen nicht initialisiert werden.")
        return

    heizung_an = False
    hysterese = 1.0  # ±1°C rund um den Sollwert

    if not os.path.exists(BME_DATEI):
        with open(BME_DATEI, "w") as f:
            f.write("Zeitstempel,Temperatur,Feuchtigkeit,Druck\n")

    print("Heizungs-Skript gestartet. Wenn kein Sollwert vorhanden ist, wird standardmäßig 20°C angenommen (nur Messen).")

    try:
        while True:
            raw_sollwert = lese_sollwert()
            if raw_sollwert is None:
                sollwert = 20.0
                regelaktiv = False
            else:
                sollwert = raw_sollwert
                regelaktiv = True

            try:
                temp = bme280.temperature
                feuchte = bme280.humidity
                druck = bme280.pressure
            except Exception as e:
                print(f"Fehler beim Lesen des BME280-Sensors: {e}")
                time.sleep(1)
                continue

            with open(BME_DATEI, "a") as f:
                f.write(f"{time.time()},{temp},{feuchte},{druck}\n")

            if regelaktiv:
                obergrenze = sollwert + hysterese
                untergrenze = sollwert - hysterese

                if heizung_an and (temp >= obergrenze):
                    pi.set_PWM_dutycycle(HEATER_PIN, 0)
                    heizung_an = False
                elif (not heizung_an) and (temp <= untergrenze):
                    pi.set_PWM_dutycycle(HEATER_PIN, 255)
                    heizung_an = True
            else:
                if heizung_an:
                    pi.set_PWM_dutycycle(HEATER_PIN, 0)
                    heizung_an = False

            time.sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        # Am Ende Heizung und Lüfter ausschalten
        pi.set_PWM_dutycycle(HEATER_PIN, 0)
        pi.set_PWM_dutycycle(FAN_PIN, 0)
        pi.stop()
        print("Heizungs-Skript beendet. Heizung und Lüfter aus.")

if __name__ == "__main__":
    main()

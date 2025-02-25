# sensor_gui/control/heating.py

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

SETPOINT_FILE = "/tmp/heater_setpoint.txt"
BME_FILE = "/tmp/bme_data.csv"

def read_setpoint():
    """Read the setpoint temperature from the setpoint file."""
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
    settings = load_settings()
    pwm_frequency = settings["pwm_frequency"]

    pi = pigpio.pi()
    if not pi.connected:
        print("Cannot connect to pigpio daemon!")
        return

    # Set the PWM frequency for both Heater and Fan
    pi.set_PWM_frequency(HEATER_PIN, pwm_frequency)
    pi.set_PWM_frequency(FAN_PIN, pwm_frequency)

    i2c = busio.I2C(board.SCL, board.SDA)
    retries = 3
    bme280 = None
    for _ in range(retries):
        try:
            bme280 = Adafruit_BME280_I2C(i2c, address=0x77)
            break
        except Exception as e:
            print(f"Failed to init BME280 at 0x77: {e}")
            time.sleep(1)

    if bme280 is None:
        print("Failed to initialize BME280 after retries.")
        return

    heater_on = False
    hysteresis = 1.0 

    # Ensure BME_FILE exists
    if not os.path.exists(BME_FILE):
        with open(BME_FILE, "w") as f:
            f.write("timestamp,temperature,humidity,pressure\n")

    print("Heating script => logging BME at ~5 Hz. If setpoint = None => measure only (default=20).")
    try:
        while True:
            raw_setpoint = read_setpoint()
            if raw_setpoint is None:
                setpoint = 20.0
                control_active = False
            else:
                setpoint = raw_setpoint
                control_active = True

            try:
                temp = bme280.temperature
                hum = bme280.humidity
                pres = bme280.pressure
            except Exception as e:
                print(f"Error reading BME280: {e}")
                time.sleep(1)
                continue

            with open(BME_FILE, "a") as f:
                f.write(f"{time.time()},{temp},{hum},{pres}\n")

            if control_active:
                upper = setpoint + hysteresis
                lower = setpoint - hysteresis
                if heater_on and (temp >= upper):
                    # Turn heater OFF => duty=0 if NOT inverting
                    pi.set_PWM_dutycycle(HEATER_PIN, 0)
                    heater_on = False
                elif not heater_on and (temp <= lower):
                    # Turn heater ON => duty=255 if NOT inverting
                    pi.set_PWM_dutycycle(HEATER_PIN, 255)
                    heater_on = True
            else:
                # Not controlling => ensure heater is off
                if heater_on:
                    pi.set_PWM_dutycycle(HEATER_PIN, 0)
                    heater_on = False

            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        # Set heater & fan OFF
        pi.set_PWM_dutycycle(HEATER_PIN, 0)
        pi.set_PWM_dutycycle(FAN_PIN, 0)
        pi.stop()
        print("Heating script ended => heater & fan OFF.")

if __name__ == "__main__":
    main()

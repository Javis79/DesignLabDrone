import time
import smbus2
import board
import busio
import adafruit_vl53l0x

# Inicjalizacja magistrali I2C1 (SDA=GPIO2, SCL=GPIO3)
i2c = busio.I2C(board.SCL, board.SDA)

# Inicjalizacja czujnika odległości VL53L0X
tof = adafruit_vl53l0x.VL53L0X(i2c)



try:
    while True:
        # Odczyt odległości z VL53L0X
        distance = tof.range
        print(f"Odległość: {distance} mm")


        time.sleep(0.5)

except KeyboardInterrupt:
    print("Zamykanie programu...")

import time
import smbus2
import math

# Adresy I2C sensorów
MPU6050_ADDR = 0x68
BMP180_ADDR = 0x77
VL53L0X_ADDR = 0x29  # Adres czujnika odległości

# Stałe dla przeliczenia wartości surowych na m/s²
GRAVITY = 9.81  # Stała grawitacyjna m/s²
ACCEL_SCALE = 16384.0  # Zakres ±2g → 1g = 16384 jednostek

# Inicjalizacja I2C
bus = smbus2.SMBus(1)  # Używamy magistrali I2C1 (SDA=GPIO2, SCL=GPIO3)

# Inicjalizacja MPU6050
def init_mpu6050():
    bus.write_byte_data(MPU6050_ADDR, 0x6B, 0x00)  # Wyłącz tryb uśpienia

# Funkcja odczytująca akcelerometr (pitch, roll)
def read_acceleration():
    acc_raw = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)
    ax = (acc_raw[0] << 8 | acc_raw[1])
    ay = (acc_raw[2] << 8 | acc_raw[3])
    az = (acc_raw[4] << 8 | acc_raw[5])
    if ax > 32767: ax -= 65536
    if ay > 32767: ay -= 65536
    if az > 32767: az -= 65536
    pitch = math.degrees(math.atan2(ay, az))
    roll = math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))
    return pitch, roll


def read_acceleration_mps2():
    acc_raw = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)

    ax = (acc_raw[0] << 8 | acc_raw[1])
    ay = (acc_raw[2] << 8 | acc_raw[3])
    az = (acc_raw[4] << 8 | acc_raw[5])

    # Obsługa wartości ujemnych (dane są w formacie 16-bit signed int)
    if ax > 32767: ax -= 65536
    if ay > 32767: ay -= 65536
    if az > 32767: az -= 65536

    # Przeliczenie wartości surowych na przyspieszenie w m/s²
    ax_mps2 = (ax / ACCEL_SCALE) * GRAVITY
    ay_mps2 = (ay / ACCEL_SCALE) * GRAVITY
    az_mps2 = (az / ACCEL_SCALE) * GRAVITY

    return ax_mps2, ay_mps2, az_mps2

# Funkcja odczytująca odległość z VL53L0X (smbus2)
def read_distance():
    try:
        bus.write_byte_data(VL53L0X_ADDR, 0x00, 0x01)  # Start pomiaru
        time.sleep(0.1)
        dist_high = bus.read_byte_data(VL53L0X_ADDR, 0x1E)
        dist_low = bus.read_byte_data(VL53L0X_ADDR, 0x1F)
        distance = (dist_high << 8) + dist_low
        return distance
    except OSError:
        return -1  # Błąd komunikacji

# Funkcja określająca kierunek przechylenia
def get_tilt_direction():
    pitch, roll = read_acceleration()

    # Określanie kierunku
    direction = ""
    if pitch > 10:
        direction += "prawo"
    elif pitch < -10:
        direction += "lewo"

    if roll > 10:
        if direction:
            direction += "-"
        direction += "tył"
    elif roll < -10:
        if direction:
            direction += "-"
        direction += "przód"

    # Określanie intensywności
    intensity = ""
    max_angle = max(abs(pitch), abs(roll))
    if max_angle < 15:
        intensity = "lekko"
    elif max_angle < 30:
        intensity = "trochę"
    elif max_angle < 45:
        intensity = "bardzo"
    else:
        intensity = "bardzo bardzo"

    return f"{intensity} {direction}"

# Sekcja main
if __name__ == "__main__":
    init_mpu6050()
    try:
        while True:
            tilt = get_tilt_direction()
            distance = read_distance()
            ax, ay, az = read_acceleration_mps2()

            print(f"Przyspieszenie: X={ax:.2f} m/s², Y={ay:.2f} m/s², Z={az:.2f} m/s²")
            print(f"Kierunek przechylenia: {tilt}")
            print(f"Odległość: {distance} mm")
            print("-" * 30)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program zakończony.")

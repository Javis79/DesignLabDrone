import smbus
import time
import math

# Adresy I2C sensorów
MPU6050_ADDR = 0x68
BMP180_ADDR = 0x77

# Inicjalizacja I2C
bus = smbus.SMBus(1)

# Inicjalizacja MPU6050
def init_mpu6050():
    bus.write_byte_data(MPU6050_ADDR, 0x6B, 0x00)  # Wyłącz tryb uśpienia

# Funkcja odczytująca temperaturę z MPU6050
def read_temperature():
    temp_raw = bus.read_i2c_block_data(MPU6050_ADDR, 0x41, 2)
    temp = ((temp_raw[0] << 8 | temp_raw[1]) / 340.0) + 36.53
    return temp

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

# Funkcja odczytująca wysokość z BMP180
def read_altitude():
    bus.write_byte_data(BMP180_ADDR, 0xF4, 0x2E)  # Pomiar temperatury
    time.sleep(0.005)
    temp_raw = bus.read_i2c_block_data(BMP180_ADDR, 0xF6, 2)

    bus.write_byte_data(BMP180_ADDR, 0xF4, 0x34)  # Pomiar ciśnienia
    time.sleep(0.005)
    pressure_raw = bus.read_i2c_block_data(BMP180_ADDR, 0xF6, 3)
    pressure = ((pressure_raw[0] << 16 | pressure_raw[1] << 8 | pressure_raw[2]) >> 8)

    pressure_sea_level = 101325  # Ciśnienie na poziomie morza w Pa
    altitude = 44330 * (1 - (pressure / pressure_sea_level)**(1/5.255))
    return altitude

# Funkcja mierząca wzniesienie akcelerometru
def calculate_vertical_motion():
    acc_raw = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)
    az_start = (acc_raw[4] << 8 | acc_raw[5])
    if az_start > 32767:
        az_start -= 65536

    acc_raw = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)
    az_now = (acc_raw[4] << 8 | acc_raw[5])
    if az_now > 32767:
        az_now -= 65536

    vertical_motion = az_now - az_start  # Różnica w przyspieszeniu
    return vertical_motion

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
            temp = read_temperature()
            altitude = read_altitude()
            tilt = get_tilt_direction()
            vertical_motion = calculate_vertical_motion()

            print(f"Temperatura: {temp:.2f}°C")
            print(f"Wysokość: {altitude:.2f} m")
            print(f"Kierunek przechylenia: {tilt}")
            print(f"Wzniesienie (akcelerometr): {vertical_motion}")
            print("-" * 30)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program zakończony.")

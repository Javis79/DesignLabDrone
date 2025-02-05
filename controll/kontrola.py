import time
import smbus2
import math
import socket
import RPi.GPIO as GPIO
import threading

# Adresy I2C sensorów
MPU6050_ADDR = 0x68
BMP180_ADDR = 0x77
VL53L0X_ADDR = 0x29  # Adres czujnika odległości

# Inicjalizacja I2C
bus = smbus2.SMBus(1)  # Używamy magistrali I2C1 (SDA=GPIO2, SCL=GPIO3)

# Ustawienia GPIO
PWM_PIN12 = 12  # Prawy tył
PWM_PIN13 = 13  # Lewy przód
GPIO_PIN23 = 23 # Lewy tył
GPIO_PIN24 = 24 # Prawy przód
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN12, GPIO.OUT)
GPIO.setup(PWM_PIN13, GPIO.OUT)
GPIO.setup(GPIO_PIN23, GPIO.OUT)
GPIO.setup(GPIO_PIN24, GPIO.OUT)

# Konfiguracja PWM dla silników
pwm12 = GPIO.PWM(PWM_PIN12, 1000)  # Prawy tył
pwm13 = GPIO.PWM(PWM_PIN13, 1000)  # Lewy przód
pwm14 = GPIO.PWM(GPIO_PIN23, 1000) # Lewy tył
pwm15 = GPIO.PWM(GPIO_PIN24, 1000) # Prawy przód
pwm12.start(50)
pwm13.start(50)
pwm14.start(50)
pwm15.start(50)

duty_cycle = 0  # Początkowa moc silników
lock = threading.Lock()

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

# Funkcja odczytująca odległość z VL53L0X
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

    return direction

# Konfiguracja serwera TCP
server_ip = '192.168.137.10'
server_port = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Serwer uruchomiony na {server_ip}:{server_port}")
print("Oczekiwanie na połączenie...")

conn, addr = server_socket.accept()
print(f"Połączono z: {addr}")

# Uruchamiamy osobny wątek do odczytu przechylenia i korekcji silników
tilt_thread = threading.Thread(target=adjust_motors_based_on_tilt, daemon=True)
tilt_thread.start()

try:
    while True:
        # Odczyt czujników
        distance = read_distance()
        print(f"Odległość: {distance} mm")

        # Odbiór komend sterowania
        data = conn.recv(1024)
        if not data:
            break
        command = data.decode('utf-8')
        print(f"Otrzymano komendę: {command}")

        with lock:
            if command == "W":  # Prawy tył
                pwm12.ChangeDutyCycle(duty_cycle + 10)
            elif command == "A":  # Lewy przód
                pwm13.ChangeDutyCycle(duty_cycle + 10)
            elif command == "S":  # Lewy tył
                pwm14.ChangeDutyCycle(duty_cycle + 10)
            elif command == "D":  # Prawy przód
                pwm15.ChangeDutyCycle(duty_cycle + 10)
            elif command == "R":  # Stop
                pwm12.ChangeDutyCycle(0)
                pwm13.ChangeDutyCycle(0)
                pwm14.ChangeDutyCycle(0)
                pwm15.ChangeDutyCycle(0)
                print("Zatrzymano silniki")
            elif command == "F":  # Przyspieszenie
                duty_cycle += 10
                pwm12.ChangeDutyCycle(duty_cycle)
                pwm13.ChangeDutyCycle(duty_cycle)
                pwm14.ChangeDutyCycle(duty_cycle)
                pwm15.ChangeDutyCycle(duty_cycle)
                print(f"Zwiększono prędkość: {duty_cycle}%")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Zamykanie serwera...")

finally:
    conn.close()
    server_socket.close()
    GPIO.cleanup()

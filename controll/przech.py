import time
import smbus2
import math
import RPi.GPIO as GPIO
from collections import deque

# Adresy I2C sensorów
MPU6050_ADDR = 0x68

# Inicjalizacja I2C
bus = smbus2.SMBus(1)  # Magistrala I2C1 (SDA=GPIO2, SCL=GPIO3)

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

# Konfiguracja PWM dla silników (start z 0%)
pwm12 = GPIO.PWM(PWM_PIN12, 1000)  # Prawy tył
pwm13 = GPIO.PWM(PWM_PIN13, 1000)  # Lewy przód
pwm14 = GPIO.PWM(GPIO_PIN23, 1000) # Lewy tył
pwm15 = GPIO.PWM(GPIO_PIN24, 1000) # Prawy przód
pwm12.start(0)
pwm13.start(0)
pwm14.start(0)
pwm15.start(0)

# Inicjalizacja MPU6050
def init_mpu6050():
    bus.write_byte_data(MPU6050_ADDR, 0x6B, 0x00)  # Wyłącz tryb uśpienia

# 🔄 **Wygładzanie odczytów (FIFO kolejka)**
pitch_values = deque(maxlen=5)  # Pamiętanie 5 ostatnich wartości
roll_values = deque(maxlen=5)

# 📏 **Martwa strefa dla przechylenia (stopnie)**
DEAD_ZONE = 8

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

    # Dodanie wartości do kolejki i uśrednienie
    pitch_values.append(pitch)
    roll_values.append(roll)
    avg_pitch = sum(pitch_values) / len(pitch_values)
    avg_roll = sum(roll_values) / len(roll_values)

    return avg_pitch, avg_roll

# 📌 **Określenie poziomu przechylenia**
def get_tilt_adjustment(value):
    """ Zwraca odpowiednie zwiększenie mocy na podstawie kąta przechylenia """
    if abs(value) < DEAD_ZONE:
        return 0  # Ignorowanie małych przechyłów
    elif 8 <= abs(value) < 30:
        return 1  # Lekkie przechylenie
    elif 30 <= abs(value) < 60:
        return 2  # Średnie przechylenie
    elif abs(value) >= 60:
        return 3  # Mocne przechylenie
    return 0

# Funkcja dostosowująca moc silników na podstawie przechylenia
def adjust_motors_based_on_tilt():
    while True:
        pitch, roll = read_acceleration()

        # Pobranie wartości zwiększenia mocy dla pitch i roll
        adjustment_pitch = get_tilt_adjustment(pitch)
        adjustment_roll = get_tilt_adjustment(roll)

        if adjustment_pitch == 0 and adjustment_roll == 0:
            # Brak przechylenia → WYŁĄCZ SILNIKI
            pwm12.ChangeDutyCycle(0)
            pwm13.ChangeDutyCycle(0)
            pwm14.ChangeDutyCycle(0)
            pwm15.ChangeDutyCycle(0)
            print(f"Silniki WYŁĄCZONE - Pitch: {pitch:.2f}, Roll: {roll:.2f}")

        else:
            # Jeśli przechylony w **prawo**, zwiększ moc prawego tyłu i przodu
            if pitch > DEAD_ZONE:
                pwm12.ChangeDutyCycle(adjustment_pitch)
                pwm15.ChangeDutyCycle(adjustment_pitch)

            # Jeśli przechylony w **lewo**, zwiększ moc lewego przodu i tyłu
            if pitch < -DEAD_ZONE:
                pwm13.ChangeDutyCycle(adjustment_pitch)
                pwm14.ChangeDutyCycle(adjustment_pitch)

            # Jeśli przechylony **do przodu**, zwiększ moc przednich silników
            if roll > DEAD_ZONE:
                pwm12.ChangeDutyCycle(adjustment_roll)
                pwm14.ChangeDutyCycle(adjustment_roll)

            # Jeśli przechylony **do tyłu**, zwiększ moc tylnych silników
            if roll < -DEAD_ZONE:
                pwm13.ChangeDutyCycle(adjustment_roll)
                pwm15.ChangeDutyCycle(adjustment_roll)

            print(f"Pitch: {pitch:.2f}, Roll: {roll:.2f}, Moc+: {max(adjustment_pitch, adjustment_roll)}%")

        time.sleep(0.1)  # Odczyt co 0.5 sekundy

# Uruchomienie układu
init_mpu6050()

try:
    adjust_motors_based_on_tilt()
except KeyboardInterrupt:
    print("Zamykanie programu...")
finally:
    GPIO.cleanup()

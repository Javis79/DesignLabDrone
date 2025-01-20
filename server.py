import socket
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

# Ustawienia GPIO
PWM_PIN12 = 12  # GPIO12, pin 32 na Raspberry Pi
PWM_PIN13 = 13  # GPIO13, pin 33 na Raspberry Pi
GPIO_PIN23 = 23  # GPIO23, pin 16 na Raspberry Pi
GPIO_PIN24 = 24  # GPIO24, pin 18 na Raspberry Pi
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN12, GPIO.OUT)
GPIO.setup(PWM_PIN13, GPIO.OUT)
GPIO.setup(GPIO_PIN23, GPIO.OUT)
GPIO.setup(GPIO_PIN24, GPIO.OUT)

# Konfiguracja PWM
pwm12 = GPIO.PWM(PWM_PIN12, 8000)  # CzÄ™stotliwoĹ›Ä‡ 1 kHz
pwm12.start(0)  # Start PWM z 0% wypeĹ‚nieniem
pwm13 = GPIO.PWM(PWM_PIN13, 8000)  # CzÄ™stotliwoĹ›Ä‡ 1 kHz
pwm13.start(0)  # Start PWM z 0% wypeĹ‚nieniem
pwm14 = GPIO.PWM(GPIO_PIN23, 8000)  # CzÄ™stotliwoĹ›Ä‡ 1 kHz
pwm14.start(0)  # Start PWM z 0% wypeĹ‚nieniem
pwm15 = GPIO.PWM(GPIO_PIN24, 8000)  # CzÄ™stotliwoĹ›Ä‡ 1 kHz
pwm15.start(0)  # Start PWM z 0% wypeĹ‚nieniem
duty_cycle = 0

# Konfiguracja serwera
server_ip = '192.168.137.10'
server_port = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Serwer uruchomiony na {server_ip}:{server_port}")
print("Oczekiwanie na poĹ‚Ä…czenie...")

conn, addr = server_socket.accept()
print(f"PoĹ‚Ä…czono z: {addr}")

try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        command = data.decode('utf-8')
        print(f"Otrzymano komende: {command}")

        if command == "W":
            print("Komenda: Do przodu")
        elif command == "A":
            print("Komenda: W lewo")
        elif command == "S":
            print("Komenda: Do tylu")
        elif command == "D":
            print("Komenda: W prawo")
        elif command == "R":
            if duty_cycle < 90:
                duty_cycle += 45
                pwm12.ChangeDutyCycle(duty_cycle)
                pwm13.ChangeDutyCycle(duty_cycle)
                pwm14.ChangeDutyCycle(duty_cycle)
                pwm15.ChangeDutyCycle(duty_cycle)
                print(f"Zwiekszanie duty_cycle: {duty_cycle}%")
            else:
                print("Duty cycle juz maksymalne (100%)")
        elif command == "F":
            if duty_cycle > 0:
                duty_cycle -= 45
                pwm12.ChangeDutyCycle(duty_cycle)
                pwm13.ChangeDutyCycle(duty_cycle)
                pwm14.ChangeDutyCycle(duty_cycle)
                pwm15.ChangeDutyCycle(duty_cycle)
                print(f"Zmniejszanie duty_cycle: {duty_cycle}%")
            else:
                print("Duty cycle juz minimalne (0%)")
        else:
            print("Nieznana komenda")
except KeyboardInterrupt:
    print("Zamykanie serwera...")
finally:
    conn.close()
    server_socket.close()

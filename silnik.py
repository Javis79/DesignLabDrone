import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

# Ustawienia GPIO
PWM_PIN12 = 12  # GPIO12, pin 32 na Raspberry Pi
PWM_PIN13 = 13  # GPIO13, pin 33 na Raspberry Pi
GPIO_PIN23 = 23 # GPIO23, pin 16 na Raspberry Pi
GPIO_PIN24 = 24 # GPIO24, pin 18 na Raspberry Pi
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

time.sleep(3)

try:
    while True:
        # ZwiÄ™ksz wypeĹ‚nienie od 0% do 100%
        for duty_cycle in range(0, 101, 5):
            pwm12.ChangeDutyCycle(duty_cycle)
            pwm13.ChangeDutyCycle(duty_cycle)
            pwm14.ChangeDutyCycle(duty_cycle)
            pwm15.ChangeDutyCycle(duty_cycle)
            time.sleep(0.5)
        # Zmniejsz wypeĹ‚nienie od 100% do 0%
        for duty_cycle in range(100, -1, -5):
            pwm12.ChangeDutyCycle(duty_cycle)
            pwm13.ChangeDutyCycle(duty_cycle)
            pwm14.ChangeDutyCycle(duty_cycle)
            pwm15.ChangeDutyCycle(duty_cycle)
            time.sleep(0.5)

        if duty_cycle < 5:
            break
except KeyboardInterrupt:
    print("Zatrzymanie programu...")
finally:
    pwm12.stop()
    pwm13.stop()
    pwm14.stop()
    pwm15.stop()
    GPIO.cleanup()

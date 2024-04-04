#!/usr/bin/python3
# Original Author: M. Heidenreich (c)
# Adapted by: Smitkumar Patel, December 2023

from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import PWMLED, Button
from threading import Thread
from time import sleep
from random import randrange
from rpi_lcd import LCD
from math import log10
from smbus import SMBus

bus = SMBus(1)
lcd = LCD()
leds = [PWMLED(26), PWMLED(13), PWMLED(6), PWMLED(5), PWMLED(23), PWMLED(16),
        PWMLED(20), PWMLED(21)]
button = Button(24)
steps = 255
fade_factor = (steps * log10(2))/(log10(steps))
ads7830_commands = (0x84, 0xc4, 0x94, 0xd4, 0xa4, 0xe4, 0xb4, 0xf4)


WHEN_RUNNING = True
delay = 0.1


def read_ads7830(input):
    bus.write_byte(0x4b, ads7830_commands[input])
    return bus.read_byte(0x4b)


def rotation_change():
    global START_LED, END_LED, count, message, direction

    START_LED, END_LED = END_LED, START_LED

    while True:
        new_count = randrange(0, len(LED_PATTERN))

        if new_count != count:
            count = new_count
            break


def print_LCD():
    while True:

        num = str(count+1)

        if count % 2 != 0:
            direction = " << "
        elif count % 2 == 0:
            direction = " >> "
        message = "PATTERN:" + num + "/8" + direction
        lcd.text(message, 1)

        lcd.text(f"B: {brightness*100:3.0f}% D: {delay:2.2f}s", 2)
        sleep(0.25)


LED_PATTERN = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0]
           ]

count = 0
START_LED = 7
END_LED = 0


def safe_exit(signum, frame):
    exit(1)


def patterns():
    global delay, brightness
    while WHEN_RUNNING:
        value = read_ads7830(0)
        delay = 0.02+0.4*value/255

        bvalue = read_ads7830(1)
        brightness = (pow(2, (bvalue/fade_factor))-1)/steps

        for id in range(8):
            leds[id].value = LED_PATTERN[count][id]*brightness

        token = LED_PATTERN[count].pop(END_LED)
        LED_PATTERN[count].insert(START_LED, token)

        sleep(delay)




signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

try:

    button.when_pressed = rotation_change
    count = randrange(0, len(LED_PATTERN))
    worker = Thread(target=patterns, daemon=True)
    print_LCD = Thread(target=print_LCD, daemon=True)
    worker.start()
    print_LCD.start()

    pause()

except KeyboardInterrupt:
    pass

finally:
    WHEN_RUNNING = False
    sleep(1.5*delay)

    lcd.clear()

    for id in range(8):
        leds[id].close()

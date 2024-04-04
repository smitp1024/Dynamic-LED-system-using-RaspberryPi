#!/usr/bin/python3
# Original Author: M. Heidenreich (c)
# Adapted by: Smitkumar Patel, December 2023

from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import LED, Button
from threading import Thread
from time import sleep
from random import randrange
from rpi_lcd import LCD


LED8 = [
    LED(26), LED(13), LED(6), LED(5),
    LED(23), LED(16), LED(20), LED(21)
      ]
button = Button(24)
lcd = LCD()

WHEN_RUNNING = True
delay = 0.1


def STYLE_CHANGE():
    global START_LED, END_LED, count, message, direction
    START_LED, END_LED = END_LED, START_LED

    while True:
        new_count = randrange(0, len(LED_PATTERN))

        if new_count != count:
            count = new_count
            break

    num = str(count+1)

    if count % 2 != 0:
        direction = " << "
    elif count % 2 == 0:
        direction = " >> "
    message = "PATTERN:" + num + "/8" + direction
    lcd.text(message, 1)


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


def patterns():
    while WHEN_RUNNING:
        for id in range(8):
            LED8[id].value = LED_PATTERN[count][id]
        token = LED_PATTERN[count].pop(END_LED)
        LED_PATTERN[count].insert(START_LED, token)
        sleep(delay)


def safe_exit(signum, frame):
    exit(1)


signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)


try:
    button.when_pressed = STYLE_CHANGE
    worker = Thread(target=patterns, daemon=True)
    worker.start()

    pause()

except KeyboardInterrupt:
    pass

finally:
    WHEN_RUNNING = False
    sleep(1.5*delay)

    for id in range(8):
        LED8[id].close()

    lcd.clear()

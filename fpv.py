#!/usr/bin/python3
import time
import traceback
import os
import sys
import RPi.GPIO as GPIO
from spyder import Globals, Encoder, ThreadWiFi, ThreadSerial, I2C, Display, Menu, ThreadCamera
from flask import Flask, render_template, Response, request
import threading
import pygame as pg


menu = {1: "System",
        2: "Kinematics",
        3: "Manual",
        4: "FPV walk",
        5: "Quit",
        10: "A1 Flash",
        11: "A1 Reset",
        12: "A2 Flash",
        13: "A2 Reset",
        14: "Sensors",
        15: "Test",
        16: "Back",
        20: "Limits",
        21: "Poses",
        22: "Tuning",
        23: "Gaits",
        24: "Back",
        30: "LED On/Off",
        31: "FAN On/Off",
        32: "Back",
        210: "Zero",
        211: "Walk",
        212: "Park",
        213: "Compact",
        214: "Back",
        220: "Height",
        221: "Length",
        222: "Speed",
        223: "Body pos",
        224: "Back",
        230: "Straight",
        231: "Strafe",
        232: "Turn",
        233: "Back"}


def systemmenu(item):
    global running, mainmenu

    if item in [10, 11, 12, 13]:
        display.show([mainmenu.fldget(item), '', 'In progress', '', ''], 2)
        if item == 10:
            os.system("sudo avrdude -p atmega328p -C /etc/avrdude.conf -c Arduino_1 -v -U flash:w:arduino1.hex:i")
            GPIO.setup(22, GPIO.OUT)
            GPIO.output(22, 1)
        if item == 11:
            GPIO.output(22, 0)
            time.sleep(.1)
            GPIO.output(22, 1)
        if item == 12:
            os.system("sudo avrdude -p atmega328p -C /etc/avrdude.conf -c Arduino_2 -v -U flash:w:arduino2.hex:i")
            GPIO.setup(26, GPIO.OUT)
            GPIO.output(26, 1)
        if item == 13:
            GPIO.output(26, 0)
            time.sleep(.1)
            GPIO.output(26, 1)

    if item == 14:
        cycle = True
        while cycle:
            display.show([mainmenu.fldget(item), 'U=' + str(g.volts) + 'V', 'I=' + str(g.amps) + 'A',
                          'T=' + str(g.temp1) + "," + str(g.temp2), 'Back'], 2)
            if g.button == 1:
                cycle = False
                g.button = 0


def testmenu():
    dsp = ''
    if i2c.read(0x11, 2, 1)[0] == 1:
        cycle = True
        scnt = False
        while cycle:
            fb = i2c.read(0x11, 1, 1)[0]
            # print(fb)
            if fb == 1:
                dsp = "LED"
            elif fb == 2:
                dsp = "RGB"
            elif fb == 3:
                dsp = "FAN"
            elif fb == 4:
                dsp = "Servos cnt"
            elif fb > 4:
                scnt = True
            elif fb == 0:
                dsp = "End"
                cycle = False
            if scnt:
                display.show(['Test', 'Servos', "found", str(fb), ''], 2)
            else:
                display.show(['Test', 'Running', dsp, str(fb), ''], 2)
            time.sleep(.1)
    else:
        display.show(['Test', '', 'ERROR', '', ''], 2)
        time.sleep(1)

    timer = time.time()
    while timer + 3 > time.time():
        display.show(['Test', 'Running', 'Ultrasonic', str(i2c.read(0x22, 1, 1)[0]), ''], 2)

    i2c.read(0x22, 2, 1)
    timer = time.time()
    while timer + 3 > time.time():
        dat = i2c.read(0x22, 3, 2)
        if dat[0] != -1:
            display.show(['Test', 'Running', 'Lidar', str(dat[0]*256+dat[1]), ''], 2)
        else:
            display.show(['Test', '', 'ERROR', '', ''], 2)
    i2c.read(0x22, 4, 1)

    timer = time.time()
    while timer + 3 > time.time():
        mpu = i2c.read(0x68, 0x3b, 6)
        display.show(['Test',
                      'IMU X = ' + str((mpu[0] << 8) | mpu[1]),
                      'IMU Y = ' + str((mpu[2] << 8) | mpu[3]),
                      'IMU Z = ' + str((mpu[4] << 8) | mpu[5]),
                      ''], 2)

    try:
        pg.mixer.music.load("march.mp3")
        display.show(['Test', 'Running', 'Player', '', ''], 2)
    except pygame.error:
        display.show(['Test', '', 'ERROR', '', ''], 2)
    pg.mixer.music.set_volume(1)
    pg.mixer.music.play()
    time.sleep(3)
    pg.mixer.music.stop()


def manual(item):
    if item == 30:
        i2c.read(0x11, 3, 1)
    if item == 31:
        i2c.read(0x11, 4, 1)


if __name__ == '__main__':
    g = Globals()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, 1)
    GPIO.setup(26, GPIO.OUT)
    GPIO.output(26, 1)
    pg.mixer.init(44100, -16, 1, 2048)
    encoder = Encoder(16, 20, 12, g)
    ThreadCamera(g)
    ThreadWiFi(g)
    ThreadSerial("/dev/serial0", 9600, g)
    i2c = I2C()
    display = Display(g)
    mainmenu = Menu(menu, g)
    display.show(mainmenu.list(), 1)
    running = True
    try:
        while running:
            display.show(mainmenu.list(), 1)
            if (g.encoder, g.button) != (0, 0):
                if g.encoder == 1:
                    mainmenu.incpos()
                if g.encoder == -1:
                    mainmenu.decpos()
                if g.button == 1:
                    mainmenu.press()
                if g.execute != 0:
                    g.button = 0
                    if g.execute == 5:
                        running = False
                    elif g.execute < 15:
                        systemmenu(g.execute)
                    elif g.execute == 15:
                        testmenu()
                    elif g.execute >= 30:
                        manual(g.execute)
                    g.execute = 0
                g.encoder = 0
                g.button = 0
            if g.uartin == 1:
                g.uartin = 0
                g.statustxt = "{:.1f}V".format(g.volts) + "-{:.1f}A".format(g.amps) +\
                    "-{:.0f}C".format(g.temp1) + "-{:.0f}C".format(g.temp2)
    except:
        print()
        traceback.print_exc()
        print()
    finally:
        display.show([], 4)
        GPIO.cleanup()
        sys.exit()

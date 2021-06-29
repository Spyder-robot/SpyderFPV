#!/usr/bin/python3
import time

from spyder import Globals, Encoder, ThreadWiFi, ThreadSerial, I2C, Display, Menu

menu = {1: "System",
        2: "Kinematics",
        3: "FPV walk",
        4: "Quit",
        10: "A1 Flash",
        11: "A1 Reset",
        12: "A2 Flash",
        13: "A2 Reset",
        14: "Sensors",
        15: "Test",
        16: "Camera",
        17: "Back",
        20: "Limits",
        21: "Poses",
        22: "Tuning",
        23: "Gaits",
        24: "Back",
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

if __name__ == '__main__':
    globvals = Globals()
    encoder = Encoder(16, 20, 12, globvals)
    ThreadWiFi(globvals)
    ThreadSerial("/dev/serial0", 9600, globvals)
    i2c = I2C()
    display = Display(globvals)
    mainmenu = Menu(menu, globvals)
    display.show(mainmenu.list(), 1)
    while True:
        display.show(mainmenu.list(), 1)
        if (globvals.encoder, globvals.button) != (0, 0):
            if globvals.encoder == 1:
                mainmenu.incpos()
            if globvals.encoder == -1:
                mainmenu.decpos()
            if globvals.button == 1:
                mainmenu.press()
            if globvals.execute != 0:
                print(globvals.execute)
                globvals.execute = 0
            globvals.encoder = 0
            globvals.button = 0
        if globvals.uartin == 1:
            globvals.uartin = 0
            globvals.statustxt = "{:.1f}V".format(globvals.volts) + "-{:.1f}A".format(globvals.amps) +\
                "-{:.0f}C".format(globvals.temp1) + "-{:.0f}C".format(globvals.temp2)

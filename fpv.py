#!/usr/bin/python3
from spyder import Globals, Encoder, ThreadWiFi, ThreadSerial


if __name__ == '__main__':
    globvals = Globals()
    encoder = Encoder(16, 20, 12, globvals)
    ThreadWiFi(globvals)
    ThreadSerial("/dev/serial0", 9600, globvals)
    while True:
        if (globvals.encoder, globvals.button) != (0, 0):
            print(globvals.encoder, globvals.button)
            globvals.encoder = 0
            globvals.button = 0
        if globvals.uartin == 1:
            globvals.uartin = 0
            print(globvals.volts, globvals.amps, globvals.temp1, globvals.temp2)

#!/usr/bin/python3
from spyder import Globals, Encoder, ThreadWiFi


if __name__ == '__main__':
    globvals = Globals()
    encoder = Encoder(16, 20, 12, globvals)
    ThreadWiFi(globvals)
    while True:
        if (globvals.encoder, globvals.button) != (0, 0):
            print(globvals.encoder, globvals.button)
            globvals.encoder = 0
            globvals.button = 0

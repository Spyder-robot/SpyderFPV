import RPi.GPIO as GPIO
from threading import Thread
import socket


class Globals:

    encoder = 0
    button = 0


class Encoder:

    def __init__(self, but, s1, s2, globs):
        self.but = but
        self.s1 = s1
        self.s2 = s2
        self.globs = globs
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([but, s1, s2], GPIO.IN)
        GPIO.add_event_detect(but, GPIO.BOTH, callback=self.onevent)
        GPIO.add_event_detect(s1, GPIO.BOTH, callback=self.onevent)
        GPIO.add_event_detect(s2, GPIO.BOTH, callback=self.onevent)
        self.enstate = 0
        self.butstateprev = GPIO.input(but)
        self.ins1prev, self.ins2prev = 1, 1
        self.activepin = 0

    def onevent(self, arg):
        self.activepin = arg
        butstate = GPIO.input(self.but)
        ins1 = GPIO.input(self.s1)
        ins2 = GPIO.input(self.s2)
        if (ins1, ins2) != (self.ins1prev, self.ins2prev):
            if abs(self.enstate) == 4:
                self.globs.encoder = int(self.enstate / 4)
            if ins1 + ins2 == 2:
                self.enstate = 0
            if abs(self.enstate) == 2 and ins1 + ins2 == 1:
                self.enstate *= 2
            if abs(self.enstate) == 1 and ins1 + ins2 == 0:
                self.enstate *= 2
            if self.enstate == 0 and ins1 + ins2 == 1:
                if ins1 == 0:
                    self.enstate = 1
                else:
                    self.enstate = -1
        if self.butstateprev == 1 and butstate == 0:
            self.globs.button = 1
        self.ins1prev, self.ins2prev = ins1, ins2
        self.butstateprev = butstate


class ThreadWiFi(Thread):

    def __init__(self, globs):
        Thread.__init__(self, target=self.wifi)
        self.daemon = True
        self.globs = globs
        self.start()

    def wifi(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', 11111))
        s.listen()
        while True:
            conn, addr = s.accept()
            print(addr)
            while conn:
                data = conn.recv(1024)
                if not data:
                    break
                cfl = False
                msgl = ''
                for c in data.decode():
                    if cfl:
                        if c == '>':
                            self.globs.encoder = int(msgl)
                            if self.globs.encoder == 2:
                                self.globs.encoder = 0
                                self.globs.button = 1
                            cfl = False
                            msgl = ''
                        else:
                            msgl = msgl + c
                    if c == '<':
                        cfl = True

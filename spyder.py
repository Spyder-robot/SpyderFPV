import traceback
import RPi.GPIO as GPIO
from threading import Thread, Condition
import socket
import serial
import time
from smbus2 import SMBus
import ST7789
from PIL import Image, ImageDraw, ImageFont
import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import numpy as np
from flask import Flask, render_template, Response, request


class Globals:

    encoder = 0
    button = 0
    amps = 0
    volts = 0
    temp1 = 0
    temp2 = 0
    uartin = 0
    wificonn = None
    statustxt = ""
    execute = 0
    app = None


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
            self.globs.wificonn, addr = s.accept()
            print(addr)
            while self.globs.wificonn:
                data = self.globs.wificonn.recv(1024)
                if data is not None:
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


class ThreadSerial(Thread):

    def __init__(self, port, baud, globs):
        self.ser = serial.Serial(port, baud)
        Thread.__init__(self, target=self.serread, args=(self.ser,))
        self.daemon = True
        self.globs = globs
        self.start()

    def serread(self, serl):
        while True:
            time.sleep(0.1)
            while serl.in_waiting > 0:
                self.globs.uartin = 1
                resp = serl.readline()
                va = resp.decode("utf-8", errors="ignore")[:-2]
                # print(va)
                if va[:3] == "<V=":
                    self.globs.volts = float(va[3:va.find(">")])
                if va[:3] == "<I=":
                    self.globs.amps = float(va[3:va.find(">")])
                if va[:4] == "<T1=":
                    self.globs.temp1 = int(float(va[4:va.find(">")]))
                if va[:4] == "<T2=":
                    self.globs.temp2 = int(float(va[4:va.find(">")]))


class I2C:

    def __init__(self):
        self.bus = SMBus(1)

    def read(self, adr, reg, bts):
        try:
            res = self.bus.read_i2c_block_data(adr, reg, bts)
        except OSError:
            res = [-1]
        return res


class Display:

    def __init__(self, globs):
        self.disp = ST7789.ST7789(port=0, cs=0, rst=23, dc=24, backlight=25, spi_speed_hz=80 * 1000 * 1000)
        self.img = Image.new('RGB', (240, 240), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.fontmenu = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        self.fontstatus = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        self.fonticon = ImageFont.truetype("/usr/share/fonts/truetype/font-awesome/fontawesome-webfont.ttf", 30)
        self.draw.text((120, 120), "SPYDER", font=self.fontmenu, fill=(255, 255, 255), anchor="mm")
        self.disp.display(self.img)
        self.globs = globs

    def drawicon(self):
        self.draw.rectangle([0, 0, 240, 35], (0, 0, 0))
        if self.globs.wificonn is not None:
            col = (0, 255, 0)
        else:
            col = (128, 128, 128)
        self.draw.text((30, 17), chr(0xf1eb), font=self.fonticon, fill=col, anchor="mm")
        if self.globs.volts > 11:
            col = (0, 255, 0)
        elif self.globs.volts > 10:
            col = (255, 255, 0)
        else:
            col = (255, 0, 0)
        if self.globs.volts == 0:
            col = (128, 128, 128)
        self.draw.text((210, 17), chr(0xf1e6), font=self.fonticon, fill=col, anchor="mm")
        msgl = "<C=1><V=" + str(self.globs.volts) + ">"
        self.wifisend(msgl)

    def drawstatus(self):
        self.draw.rectangle([0, 210, 240, 240], (0, 0, 0))
        self.draw.text((120, 210 + 15), self.globs.statustxt, font=self.fontstatus, fill=(255, 255, 255), anchor="mm")
        msgl = "<S=" + self.globs.statustxt + ">"
        self.wifisend(msgl)

    def drawlist(self, lst, mode):  # 1 - Menu, 2 - Exec, 3 - List, 4 - Bye
        self.draw.rectangle([0, 35, 240, 210], (0, 0, 0))
        msgl = ''
        for ii in range(5):
            showtext = lst[ii]
            if mode == 1:
                msgl = msgl + "<M" + str(ii) + "=" + lst[ii] + ">"
                if lst[ii].rfind('#') != -1:
                    showtext = lst[ii].replace('#', '')
                    col = (0, 255, 0)
                else:
                    col = (255, 255, 0)
            else:
                if mode == 2:
                    msgl = msgl + "<E" + str(ii) + "=" + lst[ii] + ">"
                else:
                    msgl = msgl + "<S" + str(ii) + "=" + lst[ii] + ">"
                if ii == 0:
                    col = (255, 255, 255)
                elif ii == 4:
                    col = (0, 255, 0)
                else:
                    col = (255, 255, 0)
            self.draw.text((120, 35 + ii * 35 + 17), showtext, font=self.fontmenu, fill=col, anchor="mm")
        if mode == 3:
            self.draw.rectangle([50, 103, 190, 139], outline=(255, 255, 255), width=5)
        self.wifisend(msgl)

    def show(self, lst, mode):
        if mode == 4:
            self.img = Image.new('RGB', (240, 240), color=(0, 0, 0))
            self.disp.display(self.img)
            self.disp.set_backlight(0)
        else:
            self.drawicon()
            self.drawlist(lst, mode)
            self.drawstatus()
            self.disp.display(self.img)

    def wifisend(self, msgl):
        if self.globs.wificonn is not None:
            try:
                self.globs.wificonn.send(msgl.encode())
            except:
                self.globs.wificonn = None


class Menu:

    def __init__(self, fields, globs):
        self._fields = fields
        self.curpos = 1
        self.globs = globs

    def incpos(self):
        if self._fields.get(self.curpos + 1) is not None:
            self.curpos = self.curpos + 1

    def decpos(self):
        if self._fields.get(self.curpos - 1) is not None:
            self.curpos = self.curpos - 1

    def press(self):
        if self._fields.get(self.curpos) == 'Back':
            self.curpos = int(self.curpos / 10)
            return
        if self._fields.get(self.curpos * 10) is None:
            self.globs.execute = self.curpos
        else:
            self.curpos = self.curpos * 10

    def getcur(self):
        return self._fields.get(self.curpos)

    def list(self):
        out = []
        submenu = {}
        minkey = 999
        for key in self._fields:
            if int(key / 10) == int(self.curpos / 10):
                submenu[key] = self._fields[key]
                if key < minkey:
                    minkey = key
        strt = 0
        if self.curpos > minkey + 2:
            strt = self.curpos - minkey - 2
        if self.curpos - minkey > len(submenu) - 3:
            strt = len(submenu) - 5
        if len(submenu) < 6:
            strt = 0
        for ii in range(5):
            pref = ''
            if strt + minkey + ii == self.curpos:
                pref = '#'
            opt = self._fields.get(strt + minkey + ii)
            if opt is None:
                opt = ''
            out.append(pref + opt)
        return out

    def fldget(self, ind):
        return self._fields.get(ind)


class VideoCamera(object):
    def __init__(self, flip=False):
        self.vs = PiVideoStream(resolution=(736, 416)).start()
        self.flip = flip
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


class ThreadCamera(Thread):

    def __init__(self, globs):
        Thread.__init__(self, target=self.runcam)
        self.daemon = True
        self.globs = globs
        self.start()

    def runcam(self):
        pi_camera = VideoCamera(flip=True)

        self.globs.app = Flask(__name__)

        @self.globs.app.route('/')
        def index():
            return render_template('index.html')

        def gen(camera):
            while True:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        @self.globs.app.route('/video_feed')
        def video_feed():
            return Response(gen(pi_camera),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        self.globs.app.run(host='0.0.0.0', debug=False)

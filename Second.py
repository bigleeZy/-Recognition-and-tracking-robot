#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The second edition of the program
from Tkinter import *
import tkMessageBox
import tkSimpleDialog

import struct
import sys, glob  # for listing serial ports
import dlib
import cv2
import os
from skimage import io
import numpy
#测试
try:
    import serial
except ImportError:
    tkMessageBox.showerror('Import error', 'Please install pyserial.')
    raise

connection = None

TEXTWIDTH = 40  # window width, in characters
TEXTHEIGHT = 16  # window height, in lines

VELOCITYCHANGE = 50
ROTATIONCHANGE = 50

helpText = """\





    \t\t\t\t\t\t\tIIP-Robot\t

    \tDetection And Tracking Robot
    """


class TetheredDriveApp(Tk):
    # static variables for keyboard callback -- I know, this is icky
    callbackKeyUp = False
    callbackKeyDown = False
    callbackKeyLeft = False
    callbackKeyRight = False
    callbackKeyLastDriveCommand = ''
    global j
    j = 0

    def __init__(self):
        Tk.__init__(self)
        self.title("IIP-Robot")
        self.option_add('*tearOff', FALSE)

        self.menubar = Menu()
        self.configure(menu=self.menubar)

        createMenu = Menu(self.menubar, tearoff=False)
        self.menubar.add_command(label="Connect", command=self.onConnect)
        self.menubar.add_command(label="Video", command=self.onVideo)
        self.menubar.add_command(label="Help", command=self.onHelp)
        self.menubar.add_command(label="Quit", command=self.onQuit)

        self.text = Text(self, height=TEXTHEIGHT, width=TEXTWIDTH, wrap=WORD)
        self.scroll = Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        self.scroll.pack(side=RIGHT, fill=Y)

        self.text.insert(END, helpText)

        # self.bind("<Key>", self.callbackKey)
        # self.bind("<KeyRelease>", self.callbackKey)

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                connection.write(command)
            else:
                tkMessageBox.showerror('Not connected!', 'Not connected to a robot!')
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None

        print ' '.join([str(ord(c)) for c in command])
        self.text.insert(END, ' '.join([str(ord(c)) for c in command]))
        self.text.insert(END, '\n')
        self.text.see(END)

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        global connection

        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            print "Lost connection"
            tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None
            return None
        except struct.error:
            print "Got unexpected data from serial port."
            return None

    def onConnect(self):
        global connection

        if connection is not None:
            tkMessageBox.showinfo('Oops', "You're already connected!")
            return

        try:
            ports = self.getSerialPorts()
            port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.\nAvailable options:\n' + '\n'.join(ports))
        except EnvironmentError:
            port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.')

        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print "Connected!"
                tkMessageBox.showinfo('Connected', "Connection succeeded!")
            except:
                print "Failed."
                tkMessageBox.showinfo('Failed', "Sorry, couldn't connect to " + str(port))

    def onVideo(self):
        motionChange = False
        predictor_path = "/home/lee/Software/test/shape_predictor_68_face_landmarks.dat"
        face_rec_model_path = "/home/lee/Software/test/dlib_face_recognition_resnet_model_v1.dat"
        faces_folder_path = "/home/lee/Software/pycharm_test/candidate-faces"
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(predictor_path)
        facerec = dlib.face_recognition_model_v1(face_rec_model_path)
        descriptors = []

        for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
            print("Processing file: {}".format(f))
            img = io.imread(f)
            # win.clear_overlay()
            # win.set_image(img)

            dets = detector(img, 1)
            print("Number of faces detected: {}".format(len(dets)))

            for k, d in enumerate(dets):
                shape = predictor(img, d)
                # win.clear_overlay()
                # win.add_overlay(d)
                # win.add_overlay(shape)

                face_descriptor = facerec.compute_face_descriptor(img, shape)
                # print ("face_descriptor: {}".format(face_descriptor))

                v = numpy.array(face_descriptor)
                # print ("v: {}".format(v))
                descriptors.append(v)
                # print ("descriptors: {}".format(descriptors))

        win = dlib.image_window()
        cap = cv2.VideoCapture(0)
        c = 1
        time = 10
        while cap.isOpened():

            ret, cv_img = cap.read()
            if cv_img is None:
                break

            image = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
            win.clear_overlay()
            win.set_image(image)
            dets = detector(image, 0)
            dist = []
            # print("Number of faces detected: {}".format(len(dets)))
            # lists = [[0 for k in range(4)] for j in range(10)]
            if (c % time == 0):
                for k, d in enumerate(dets):
                    # print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                    #     i, d.left(), d.top(), d.right(), d.bottom()))

                    shape1 = predictor(image, d)
                    # print("Part 0: {}, Part 1: {}, Part 2: {} ...".format(shape.part(0),  shape.part(1), shape.part(2)))
                    win.clear_overlay()
                    win.add_overlay(d)
                    win.add_overlay(shape1)
                    face_descriptor1 = facerec.compute_face_descriptor(image, shape1)
                    # print ("face_descriptor1: {}".format(face_descriptor1))

                    d_test = numpy.array(face_descriptor1)
                    # print ("d_test: {}".format(d_test))

                    for i in descriptors:
                        dist_ = numpy.linalg.norm(i - d_test)
                        dist.append(dist_)
                    # print("dist: {}".format(dist))
                    candidate = ['张丽梅', '丁高兴', '徐科杰', '金莹莹', '李政英',
                                 '石光耀', '陈美利', '段宇乐', '李宗辉', '陈杰']
                    c_d = dict(zip(candidate, dist))
                    cd_sorted = sorted(c_d.iteritems(), key=lambda d: d[1])
                    # print (cd_sorted)
                    if (((cd_sorted[1][1] - cd_sorted[0][1]) < 0.1) & (cd_sorted[0][1] > 0.381)):
                        print "\n 这个人是：陌生人"
                        j = -1
                        x = -1
                    else:
                        print "\n 这个人是：", cd_sorted[0][0]

                        if (cd_sorted[0][0] == '李政英'):
                            j = d.bottom() - d.top()
                            x = d.left()
                        elif (cd_sorted[0][0] == '陈美利'):
                            j = d.bottom() - d.top()
                            x = d.left()
                        else:
                            j = -1
                            x = -1

                if len(dets) == 0:
                    self.callbackKeyLeft = False
                    self.callbackKeyRight = False
                    self.callbackKeyDown = False
                    self.callbackKeyUp = False
                    motionChange = True
                else:
                    if x > 300:
                        self.callbackKeyRight = True
                        motionChange = True
                    elif 0 < x < 180:
                        self.callbackKeyLeft = True
                        motionChange = True
                    elif 180 < x < 300:
                        self.callbackKeyLeft = False
                        self.callbackKeyRight = False
                        motionChange = True
                        if j > 140:
                            self.callbackKeyDown = True
                            motionChange = True
                        elif 0 < j < 110:
                            self.callbackKeyUp = True
                            motionChange = True
                        elif 110 < j < 140:
                            self.callbackKeyDown = False
                            self.callbackKeyUp = False
                            motionChange = True

                if motionChange == True:
                    velocity = 0
                    velocity += VELOCITYCHANGE if self.callbackKeyUp is True else 0
                    velocity -= VELOCITYCHANGE if self.callbackKeyDown is True else 0
                    rotation = 0
                    rotation += ROTATIONCHANGE if self.callbackKeyLeft is True else 0
                    rotation -= ROTATIONCHANGE if self.callbackKeyRight is True else 0

                    # compute left and right wheel velocities
                    vr = velocity + (rotation / 2)
                    vl = velocity - (rotation / 2)

                    # create drive command
                    cmd = struct.pack(">Bhh", 145, vr, vl)
                    if cmd != self.callbackKeyLastDriveCommand:
                        self.sendCommandRaw(cmd)
                        self.callbackKeyLastDriveCommand = cmd
            c = c + 1
            # win.clear_overlay()
            # win.set_image(img)
            # win.add_overlay(dets)

        cap.release()

    def onHelp(self):
        tkMessageBox.showinfo('Help', helpText)

    def onQuit(self):
        if tkMessageBox.askyesno('Really?', 'Are you sure you want to quit?'):
            self.destroy()

    def getSerialPorts(self):
        """Lists serial ports
        From http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == "__main__":
    app = TetheredDriveApp()
    app.mainloop()
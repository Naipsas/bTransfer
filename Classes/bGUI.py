#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Naipsas - Btc Sources
# bTransfer
# Started on Jan 2019

import os
import time

import socket
import struct
import threading

import urllib.error
import urllib.request

from Classes.Parser import Parser

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QFileDialog
from PyQt5.QtWidgets import QPushButton, QLabel, QListWidget, QLineEdit, QProgressBar

if __name__ == '__main__':
    print("Esta clase no es ejecutable")



# https://stackoverflow.com/questions/12083034/pyqt-updating-gui-from-a-callback
class Recv_File_Task(QtCore.QThread):

    progress = QtCore.pyqtSignal(float)
    speed = QtCore.pyqtSignal(str)
    recvfile = QtCore.pyqtSignal(str)

    speedacc = []
    size = 0

    port = 0

    filename = ""

    def setPort(self, port):
        self.port = port

    def __setProgress(self, amount):
        if self.size != 0:
            self.progress.emit(float(amount) / self.size)
        else:
            self.progress.emit(0)

    def __setSpeed(self, data, time):
        speed = data / time
        avg = self.__calculateAvg(speed)
        units = "Bps"
        prefix = ""
        if avg > 1000:
            avg /= 1024
            prefix = "K"
        if avg > 1000:
            avg /= 1024
            prefix = "M"
        avg = self.__truncate(avg)
        avg = str(avg) + prefix + units
        self.speed.emit(avg)

    def __calculateAvg(self, speed):
        if len(self.speedacc) > 5:
            self.speedacc.remove(self.speedacc[0])

        self.speedacc.append(speed)
        avg = sum(self.speedacc) / len(self.speedacc)
        return avg

    def __truncate(self, number):
        return '%.2f'%(number)

    def __recvData(self):
        lengthbuf = self.__recvall(4)
        if lengthbuf is not None:
            length, = struct.unpack('!I', lengthbuf)
            return self.__recvall(length)
        else:
            return False

    def __recvall(self, count):
        buf = b''
        while count:
            newbuf = self.c.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def __recvHeader(self, data):
        line = data.decode("utf-8").split(":")
        if line[0] == "Name":
            self.filename = line[1]
            self.f = open(os.path.join(os.getcwd(), self.filename), 'wb')
            self.recvfile.emit(self.filename)
        elif line[0] == "Size":
            self.size = int(line[1])
        else:
            print("ERROR: " + "".join(line))

    def run(self):

        while True:

            self.s = socket.socket()
            self.s.bind(('0.0.0.0', int(self.port)))
            self.s.listen(1)

            self.c, addr = self.s.accept()

            stage = 0
            acc = 0

            self.__setProgress(acc)

            l = self.__recvData()
            while (l):
                start_time = time.perf_counter()
                if stage < 2:
                    self.__recvHeader(l)
                    stage += 1
                else:
                    self.f.write(l)
                    acc += len(l)
                    self.__setProgress(acc)
                #l = c.recv(1024)
                elapsed_time = time.perf_counter() - start_time
                self.__setSpeed(len(l), elapsed_time)
                l = self.__recvData()

            self.f.close()
            self.c.close()
            self.s.shutdown(socket.SHUT_WR)
            self.s.close()
            stage = 0
            acc = 0

class Send_File_Task(QtCore.QThread):

    progress = QtCore.pyqtSignal(float)
    speed = QtCore.pyqtSignal(str)

    speedacc = []
    size = 0

    port = 0
    ip = ""
    file = ""

    def __init__(self):
        super(Send_File_Task, self).__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setTarget(self, ip, port):
        self.ip = ip
        self.port = int(port)

    def setFile(self, file):
        self.file = file
        self.size = os.path.getsize(file)

    def __sendHeader(self, name, value):
        message = (name + ":" + value).encode('utf-8')
        self.__sendData(message)

    def __sendData(self, data):
        length = len(data)
        self.s.sendall(struct.pack('!I', length))
        self.s.sendall(data)

    def __setProgress(self, amount):
        if self.size != 0:
            self.progress.emit(float(amount) / self.size)
        else:
            self.progress.emit(0)

    def __setSpeed(self, data, time):
        speed = data / time
        avg = self.__calculateAvg(speed)
        units = "Bps"
        prefix = ""
        if avg > 1000:
            avg /= 1024
            prefix = "K"
        if avg > 1000:
            avg /= 1024
            prefix = "M"
        avg = self.__truncate(avg)
        avg = str(avg) + prefix + units
        self.speed.emit(avg)

    def __calculateAvg(self, speed):
        if len(self.speedacc) > 49:
            self.speedacc.remove(self.speedacc[0])

        self.speedacc.append(speed)
        avg = sum(self.speedacc) / len(self.speedacc)
        return avg

    def __truncate(self, number):
        return '%.2f'%(number)

    def run(self):

        #host = socket.gethostname()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))

        self.__sendHeader("Name", self.file.split("/")[-1])
        self.__sendHeader("Size", str(self.size))
        f = open(self.file,'rb')
        l = f.read(1024)
        acc = 0
        self.__setProgress(acc)
        while (l):
            start_time = time.perf_counter()
            self.__sendData(l)
            acc += len(l)
            self.__setProgress(acc)
            l = f.read(1024)
            elapsed_time = time.perf_counter() - start_time
            self.__setSpeed(len(l), elapsed_time)
        f.close()
        self.s.shutdown(socket.SHUT_WR)
        self.s.close()

class bGUI:

    def __init__(self):

        self.receiver = False
        self.port = ""

        self.__initUI()

    def __initUI(self):

        app = QApplication([])

        window = QWidget()
        layout = QGridLayout()
        layout.setSpacing(10)

        # First row
        send_title_label = QLabel("Enviar ficheros")
        send_title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(send_title_label, 1, 0)
        recv_title_label = QLabel("Recibir ficheros")
        recv_title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(recv_title_label, 1, 1)

        # First we prepare the left side with several widgets
        leftside = QGridLayout()

        # First row
        leftside.addWidget(QLabel("IP destino: "), 1, 0)
        self.ip_lineedit = QLineEdit()
        self.ip_lineedit.setPlaceholderText("Ejemplo: 8.8.8.8")
        self.ip_lineedit.textChanged.connect(lambda text, le=self.ip_lineedit: self.__ipChanged(le, text))
        leftside.addWidget(self.ip_lineedit, 1, 1)
        # Second row
        leftside.addWidget(QLabel("Puerto (TCP): "), 2, 0)
        self.sd_port_lineedit = QLineEdit()
        self.sd_port_lineedit.setPlaceholderText("Ejemplo: 20288")
        self.sd_port_lineedit.textChanged.connect(lambda text, le=self.sd_port_lineedit: self.__portChanged(le, text))
        leftside.addWidget(self.sd_port_lineedit, 2, 1)
        # Third row
        leftside.addWidget(QLabel("Fichero: "), 3, 0)
        file_button = QPushButton("Seleccionar")
        file_button.clicked.connect(self.__selectFile)
        leftside.addWidget(file_button, 3, 1, 1, 1, Qt.AlignCenter)
        self.file_label = QLabel("No seleccionado")
        self.file_label.setAlignment(Qt.AlignCenter)
        leftside.addWidget(self.file_label, 4, 0, 1, 2)
        # Third row
        leftside.addWidget(QLabel("Progreso: "), 5, 0)
        self.sd_speed_label = QLabel("No enviando")
        #sd_speed_label.setAlignment(Qt.AlignCenter)
        leftside.addWidget(self.sd_speed_label, 5, 1)
        self.send_progressbar = QProgressBar()
        leftside.addWidget(self.send_progressbar, 6, 0, 1, 2)

        # Compose it all and add to the main grid
        # https://www.pythoncentral.io/pyside-pyqt-tutorial-the-qlistwidget/
        layout.addLayout(leftside, 2, 0)

        # Now we prepare the right side
        rightside = QGridLayout()

        # First row
        yourip_label = QLabel("Tu IP: " + str(self.__checkPublicIP()))
        rightside.addWidget(yourip_label, 1, 0, 1, 2)
        # Second row
        rightside.addWidget(QLabel("Puerto (TCP): "), 2, 0)
        self.rc_port_lineedit = QLineEdit()
        self.rc_port_lineedit.setPlaceholderText("Ej: 30288. ¡Abre el puerto en tu router!")
        #self.rc_port_lineedit.textChanged.connect(self.__portChanged)
        self.rc_port_lineedit.textChanged.connect(lambda text, le=self.rc_port_lineedit: self.__portChanged(le, text))
        rightside.addWidget(self.rc_port_lineedit, 2, 1, 1, 1)
        self.recv_label = QLabel("No se está recibiendo nada")
        self.recv_label.setAlignment(Qt.AlignCenter)
        rightside.addWidget(self.recv_label, 3, 0, 2, 2)
        # Third row
        rightside.addWidget(QLabel("Progreso: "), 5, 0)
        self.rc_speed_label = QLabel("No recibiendo")
        #rc_speed_label.setAlignment(Qt.AlignCenter)
        rightside.addWidget(self.rc_speed_label, 5, 1)
        self.recv_progressbar = QProgressBar()
        rightside.addWidget(self.recv_progressbar, 6, 0, 1, 2)

        #layout.addWidget(QListWidget(), 2, 1)
        layout.addLayout(rightside, 2, 1)

        # Third row
        self.send_button = QPushButton('Enviar')
        self.send_button.clicked.connect(self.__sendFile)
        layout.addWidget(self.send_button, 3, 0, 1, 1, Qt.AlignCenter)

        self.enable_button = QPushButton('Activar')
        self.enable_button.clicked.connect(self.__toggleReceiver)
        layout.addWidget(self.enable_button, 3, 1, 1, 1, Qt.AlignCenter)

        # Server - receive file
        self._threadRc = Recv_File_Task()
        self._threadRc.progress.connect(lambda progress, le=self.recv_progressbar: self.__updateProgressBar(le, progress))
        self._threadRc.speed.connect(lambda speed, le=self.rc_speed_label: self.__updateSpeed(le, speed))
        self._threadRc.recvfile.connect(self.__recvFileName)

        # Client - send file
        self._threadSd = Send_File_Task()
        self._threadSd.progress.connect(lambda progress, le=self.send_progressbar: self.__updateProgressBar(le, progress))
        self._threadSd.speed.connect(lambda speed, le=self.sd_speed_label: self.__updateSpeed(le, speed))

        window.setMinimumWidth(650)
        window.setWindowTitle('bTransfer')
        window.setLayout(layout)
        window.show()
        app.exec_()

    def __checkPublicIP(self):
        try:
            hdr = {'User-Agent':'Mozilla/5.0'}
            req = urllib.request.Request('http://www.cualesmiip.com', headers=hdr)

            try:
                page = urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                #print(e.fp.read())
                pass

            myParser = Parser()
            myParser.feed(str(page.read()))
            page.close()

            return myParser.result

        except Exception as e:
            #page.close()
            print(e)

    def __ipChanged(self, widget, text):
        # Here we have no checks yet
        self.ip = text

    def __recvFileName(self, name):
        self.recv_label.setText("Recibiendo: " + name)

    def __portChanged(self, widget, text):
        try:
            if int(text) > 65356:
                final = "65535"
            elif int(text) <= 0:
                final = "20000"
            else:
                final = text

            widget.setText(final)
            self.port = final

        except Exception as e:
            widget.setText("0")

    def __toggleReceiver(self):

        if (self.receiver == False) and (self.port != ""):
            self.enable_button.setText("Desactivar")

            # Enable TCP server
            self._threadRc.setPort(self.port)
            self._threadRc.start()

            self.receiver = True

        else:
            self.enable_button.setText("Activar")

            # Disable TCP server
            self._threadRc.exit()

            self.receiver = False

    def __updateProgressBar(self, bar, amount):
        bar.setValue(amount * 100)

    def __updateSpeed(self, label, speed):
        label.setText(speed)

    def __sendFile(self):

        self._threadSd.setTarget(self.ip, self.port)
        self._threadSd.setFile(self.filename[0])
        self._threadSd.start()

    def __selectFile(self):

        self.filename = QFileDialog.getOpenFileName(QWidget(), 'Selecciona el fichero a enviar...',
         'c:\\', "Todos los ficheros (*.*)")

        if self.filename:
            self.file_label.setText(self.filename[0])
            #self.file_label.repaint()


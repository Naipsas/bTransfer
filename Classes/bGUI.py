#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Naipsas - Btc Sources
# bTransfer
# Started on Jan 2019

import socket
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

    progress = QtCore.pyqtSignal(int)

    def run(self):
        # do some functionality
        for i in range(10000):
            self.updated.emit(str(i))

class Send_File_Task(QtCore.QThread):

    progress = QtCore.pyqtSignal(int)

    def run(self):
        # do some functionality
        for i in range(10000):
            self.updated.emit(str(i))

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
        ip_lineedit = QLineEdit()
        ip_lineedit.setPlaceholderText("Ejemplo: 8.8.8.8")
        leftside.addWidget(ip_lineedit, 1, 1)
        # Second row
        leftside.addWidget(QLabel("Puerto (TCP): "), 2, 0)
        self.sd_port_lineedit = QLineEdit()
        self.sd_port_lineedit.setPlaceholderText("Ejemplo: 20288")
        #self.sd_port_lineedit.textChanged.connect(self.__portChanged)
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
        sd_speed_label = QLabel("No enviando")
        #sd_speed_label.setAlignment(Qt.AlignCenter)
        leftside.addWidget(sd_speed_label, 5, 1)
        leftside.addWidget(QProgressBar(), 6, 0, 1, 2)

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
        recv_label = QLabel("No se está recibiendo nada")
        recv_label.setAlignment(Qt.AlignCenter)
        rightside.addWidget(recv_label, 3, 0, 2, 2)
        # Third row
        rightside.addWidget(QLabel("Progreso: "), 5, 0)
        rc_speed_label = QLabel("No enviando")
        #rc_speed_label.setAlignment(Qt.AlignCenter)
        rightside.addWidget(rc_speed_label, 5, 1)
        rightside.addWidget(QProgressBar(), 6, 0, 1, 2)

        #layout.addWidget(QListWidget(), 2, 1)
        layout.addLayout(rightside, 2, 1)

        # Third row
        send_button = QPushButton('Enviar')
        layout.addWidget(send_button, 3, 0, 1, 1, Qt.AlignCenter)
        self.enable_button = QPushButton('Activar')
        self.enable_button.clicked.connect(self.__toggleReceiver)
        layout.addWidget(self.enable_button, 3, 1, 1, 1, Qt.AlignCenter)


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

    def __portChanged(self, widget, text):
        try:
            if int(text) > 65356:
                widget.setText("65535")
            elif int(text) <= 0:
                widget.setText("20000")

            self.port = text

        except Exception as e:
            widget.setText("20000")

    def __toggleReceiver(self):

        if self.receiver == False:
            self.enable_button.setText("Desactivar")

            # Enable TCP server
            self.s = socket.socket()
            self.host = socket.gethostname()
            self.s.bind((self.host, int(self.port)))
            self.s.listen(1)

        else:
            self.enable_button.setText("Activar")

            # Disable TCP server
            self.s.close()

        self.receiver = not self.receiver

    def __waitForFile(self):

        stage = 0

        while True:
            c, addr = self.s.accept()
            #print 'Got connection from', addr
            #print "Receiving..."
            l = c.recv(1024)
            while (l):
                #print "Receiving..."
                if stage == 0:
                    f = open("/home/btc/Escritorio/" + str(l), 'wb')
                    stage += 1
                else:
                    f.write(l)
                l = c.recv(1024)
            f.close()
            #print "Done Receiving"
            #c.send('Thank you for connecting')
            c.close()

    def __selectFile(self):

        self.filename = QFileDialog.getOpenFileName(QWidget(), 'Selecciona el fichero a enviar...',
         'c:\\', "Todos los ficheros (*.*)")

        if self.filename:
            self.file_label.setText(self.filename[0])
            #self.file_label.repaint()


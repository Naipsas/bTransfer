#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Naipsas - Btc Sources
# bTransfer
# Started on Jan 2019

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QFileDialog
from PyQt5.QtWidgets import QPushButton, QLabel, QListWidget, QLineEdit, QProgressBar

if __name__ == '__main__':
    print("Esta clase no es ejecutable")

class bGUI:

    def __init__(self):

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

        # Second row, first we prepare the left side with several widgets
        leftside = QGridLayout()

        # First row
        leftside.addWidget(QLabel("IP destino: "), 1, 0)
        ip_lineedit = QLineEdit()
        ip_lineedit.setPlaceholderText("Ejemplo: 8.8.8.8")
        leftside.addWidget(ip_lineedit, 1, 1)
        # Second row
        leftside.addWidget(QLabel("Fichero: "), 2, 0)
        file_button = QPushButton("Seleccionar")
        leftside.addWidget(file_button, 2, 1)
        file_label = QLabel("No seleccionado")
        file_label.setAlignment(Qt.AlignCenter)
        leftside.addWidget(file_label, 3, 0, 1, 2)
        # Third row
        leftside.addWidget(QLabel("Progreso: "), 4, 0)
        speed_label = QLabel("No enviando")
        speed_label.setAlignment(Qt.AlignCenter)
        leftside.addWidget(speed_label, 4, 1)
        leftside.addWidget(QProgressBar(), 5, 0, 1, 2)

        # Compose it all
        # https://www.pythoncentral.io/pyside-pyqt-tutorial-the-qlistwidget/
        layout.addLayout(leftside, 2, 0)
        layout.addWidget(QListWidget(), 2, 1)

        # Third row
        layout.addWidget(QPushButton('Enviar'), 3, 0)

        window.setWindowTitle('bTransfer')
        window.setLayout(layout)
        window.show()
        app.exec_()
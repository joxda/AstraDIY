#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt
from AstraGpio import AstraGpio
from AstraCommonHmi import dataMenu


class GpioControl(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name=name
        self.gpio = AstraGpio(name)
        self.initUI()

    def initUI(self):
        #self.setStyleSheet("border: 1px solid black;") 
        
        # Zone de texte initiale
        self.TextName = QLabel(self.name, self)
        #self.TextName.setReadOnly(True)
        self.TextName.setFixedWidth(100)

        # Bouton On/Off
        self.toggle_button = QPushButton('Off set On', self)
        self.toggle_button.setFixedWidth(100)
        self.toggle_button.setStyleSheet("border: 1px solid black;") 
        self.set_togglebuttonText()
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_action)

        # Layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.TextName)
        layout.addWidget(self.toggle_button)
        self.setLayout(layout)

    def set_togglebuttonText(self):
        if self.gpio.is_on():
            self.toggle_button.setText('On Set Off')
            self.toggle_button.setStyleSheet("background-color: #f75457; border: 1px solid black;")
        else:
            self.toggle_button.setText('Off Set On')
            self.toggle_button.setStyleSheet("background-color: #3cbaa2; border: 1px solid black;") 


    def toggle_action(self):
        self.gpio.switch_onoff()
        self.set_togglebuttonText()
        self.gpio.print_status()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)

        self.widgets = []
        for name in ["AstraDc1", "AstraDc2", "AstraDc3"]:
            wiget=GpioControl(name)
            self.widgets.append(wiget)
            self.main_layout.addWidget(wiget)
        
        self.setLayout(self.main_layout)
        self.setWindowTitle('AstrAlim')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()


    sys.exit(app.exec_())


#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt
from AstraGpio import AstraGpio
from AstraCommonHmi import dataMenu, AnimatedToggleButton


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
        self.toggle_button = AnimatedToggleButton(self, self.gpio.is_on(), self.toggle_action)

        # Layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.TextName)
        layout.addWidget(self.toggle_button)
        self.setLayout(layout)

    def toggle_action(self, state):
        if self.toggle_button.slider.isChecked():
            self.gpio.set_on()
        else:
            self.gpio.set_off()
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


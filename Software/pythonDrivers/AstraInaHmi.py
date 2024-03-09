#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt
from AstraIna import AstraIna
from AstraDataMenu import dataMenu


class ina219Frame(QFrame):
    def __init__(self, ina219):
        super().__init__()
        self.ina219 = ina219
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("border: 1px solid black;") 
        
        label = QLabel(self.ina219.get_name()) 
        label.setAlignment(Qt.AlignCenter)        
        label.adjustSize()
        # Voltage
        self.textVoltage = dataMenu("Tension", "V")
        self.textVoltage.setFixedWidth(80,70,50)
        self.textVoltage.setReadOnly(True)

        # Current 
        self.textCurrent = dataMenu("Courant", "mA")
        self.textCurrent.setFixedWidth(80,70,50)
        self.textCurrent.setReadOnly(True)

        # PowerQT
        self.textEnergie = dataMenu("Energie", "Ah")
        self.textEnergie.setFixedWidth(80,70,50)
        self.textEnergie.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.textVoltage)
        layout.addWidget(self.textCurrent)
        layout.addWidget(self.textEnergie)
        layout.setSpacing(0)
        layout.setContentsMargins(1, 1, 1, 1)  # Set the margins inside the frame
        self.setLayout(layout)
        self.setFixedSize(230, 160)

    def update_text_fields(self):
        bus_voltage = self.ina219.voltage()
        current = self.ina219.current()
        energie = self.ina219.energie()/3600/1000

        self.textVoltage.setText(f"{bus_voltage:+.1f}")
        self.textCurrent.setText(f"{current:+.1f}")
        if energie < 100:
            self.textEnergie.setText(f"{energie:.3f}")
        elif energie < 500:
            self.textEnergie.setText(f"{energie:.2f}")
        elif energie < 1000:
            self.textEnergie.setText(f"{energie:.1f}")
        else:
            energie=int(energie/1000)
            self.textEnergie.setText(f"{energie}k")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)

        self.widgets = []

        for name in AstraIna.getListNames():
            wiget=ina219Frame(AstraIna(name=name))
            self.widgets.append(wiget)
            self.main_layout.addWidget(wiget)
        
        self.setLayout(self.main_layout)
        self.setWindowTitle('AstrAlim')


        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [widget.update_text_fields() for widget in self.widgets])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def closeEvent(self, event):
        AstraIna.exitAll()
        #os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()


    sys.exit(app.exec_())


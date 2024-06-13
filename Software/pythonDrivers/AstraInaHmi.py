#!/bin/env python3
import sys
import os
import signal
import math
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt
from AstraIna import AstraIna
from AstraCommonHmi import dataMenu


class ina219Frame(QFrame):
    def __init__(self, ina219):
        super().__init__()
        self.ina219 = ina219
        #self.setStyleSheet("border: 1px solid black;") 
        
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

        # Integration Time
        self.intPeriod = dataMenu("IntPeriod", "s")
        self.intPeriod.setFixedWidth(80,70,50)
        self.intPeriod.setReadOnly(True)

        self.styleElement = "background: transparent; background-color: transparent; border: none; color: black;"
        self.textVoltage.setStyleSheet(self.styleElement)
        self.textCurrent.setStyleSheet(self.styleElement)
        self.textEnergie.setStyleSheet(self.styleElement)
        self.intPeriod.setStyleSheet(self.styleElement)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(label)
        layout.addWidget(self.textVoltage)
        layout.addWidget(self.textCurrent)
        layout.addWidget(self.textEnergie)
        layout.addWidget(self.intPeriod)
        layout.setSpacing(0)
        #layout.setContentsMargins(1, 1, 1, 1)  # Set the margins inside the frame
        self.setLayout(layout)
        #self.setFixedSize(230, 160)
        self.setStyleSheet("border: 1px solid black;") 

    def update_text_fields(self):
        bus_voltage = self.ina219.voltage()
        current = self.ina219.current()
        energie = self.ina219.energie()/3600/1000
        intPeriods = int(self.ina219.intPeriod())
        intPeriodm = int(intPeriods/60)
        intPeriods %= 60
        intPeriodh = int(intPeriodm/60)
        intPeriodm %= 60

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
        self.intPeriod.setText(f"{intPeriodh:2d}:{intPeriodm:2d}:{intPeriods:2d}")

class MainInaWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Layout de type grille
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(0)

        self.widgets = []
        listIna =  AstraIna.getListNames()

        # Calculer le nombre de lignes et de colonnes pour obtenir une forme carrée
        n = len(listIna)
        rows = cols = math.ceil(math.sqrt(n))

        for index, name in enumerate(listIna):
            row = index // cols
            col = index % cols
            widget=ina219Frame(AstraIna(name=name))
            self.widgets.append(widget)
            self.main_layout.addWidget(widget, row, col)
        
        self.setLayout(self.main_layout)
        self.setWindowTitle('AstrAlimIna')


        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [widget.update_text_fields() for widget in self.widgets])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def closeEvent(self, event):
        AstraIna.exitAll()
        #os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainInaWindow()
    main_window.show()


    sys.exit(app.exec_())


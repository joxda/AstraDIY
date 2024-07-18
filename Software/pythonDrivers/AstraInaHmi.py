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

def formatEnergie(energie):
    retval=""
    if not isinstance(energie, (int, float)):
        retval=energie
    elif energie < 100:
        retval=f"{energie:.3f}"
    elif energie < 500:
        retval=f"{energie:.2f}"
    elif energie < 1000:
        retval=f"{energie:.1f}"
    else:
        energie=int(energie/1000)
        retval=f"{energie}k"
    return retval


class ina219Frame(QFrame):
    def __init__(self, ina219, parent=None):
        super().__init__(parent)
        self.ina219 = ina219
        #self.setStyleSheet("border: 1px solid black;") 
        
        label = QLabel(self.ina219.get_name(), parent=self) 
        label.setAlignment(Qt.AlignCenter)        
        label.adjustSize()
        # Voltage
        self.textVoltage = dataMenu("Tension", "V", parent=self)
        self.textVoltage.setFixedWidth(80,70,50)
        self.textVoltage.setReadOnly(True)

        # Current 
        self.textCurrent = dataMenu("Courant", "mA", parent=self)
        self.textCurrent.setFixedWidth(80,70,50)
        self.textCurrent.setReadOnly(True)

        # PowerQT
        self.textEnergie = dataMenu("Energie", "Ah", parent=self)
        self.textEnergie.setFixedWidth(80,70,50)
        self.textEnergie.setReadOnly(True)

        # Integration Time
        self.intPeriod = dataMenu("IntPeriod", "s", parent=self)
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
        intPeriods = int(self.ina219.intPeriod())
        intPeriodm = int(intPeriods/60)
        intPeriods %= 60
        intPeriodh = int(intPeriodm/60)
        intPeriodm %= 60

        self.textVoltage.setText(f"{bus_voltage:+.1f}")
        self.textCurrent.setText(f"{current:+.1f}")
        self.textEnergie.setText(formatEnergie(self.ina219.energie()/3600/1000))
        self.intPeriod.setText(f"{intPeriodh:2d}:{intPeriodm:2d}:{intPeriods:2d}")

    def get_totalEnergieAh(self):
        return self.ina219.get_totalEnergie()/3600/1000

class MainInaWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


        # Layout de type grille
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(0)

        # Add QLabel at the top
        self.TotalEnergie = dataMenu(" Total Energie = ", "Ah ", parent=self)
        self.TotalEnergie.setReadOnly(True)
        self.TotalEnergie.setStyleSheet("border: 1px solid black;") 
        self.main_layout.addWidget(self.TotalEnergie, 0, 1)


        self.widgets = []
        listIna =  AstraIna.getListNames()

        # Calculer le nombre de lignes et de colonnes pour obtenir une forme carrée
        n = len(listIna) + 1
        rows = cols = math.ceil(math.sqrt(n))

        for index, name in enumerate(listIna):
            row = (index // cols) +1 
            col = index % cols
            widget=ina219Frame(AstraIna(name=name), parent=self)
            self.widgets.append(widget)
            self.main_layout.addWidget(widget, row, col)
         
        self.setLayout(self.main_layout)
        self.setWindowTitle('AstrAlimIna')


        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [self.update_text_fields()])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def  update_text_fields(self):
        self.TotalEnergie.setText(formatEnergie(self.widgets[1].get_totalEnergieAh()))
  
        for widget in self.widgets:
            widget.update_text_fields() 

    def closeEvent(self, event):
        AstraIna.exitAll()
        #os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainInaWindow()
    main_window.show()


    sys.exit(app.exec_())


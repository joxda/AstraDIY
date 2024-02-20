#!/bin/env python3
import sys
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QFrame
from PyQt5.QtCore import Qt
from ina219 import INA219
from AstraGpio import AstraGpio
from AstraPwm import AstraPwm


class dataMenu(QWidget):
    def __init__(self, label, unit):
        self.unit=unit
        self.label=label
        super().__init__()
        self.initUI()

    def initUI(self):
        self.type_label = QLabel(self.label, self)  
        self.type_label.setAlignment(Qt.AlignCenter)
        #self.type_label.setFixedHeight(50)

        self.line_edit = QLineEdit(self)
        #self.line_edit.setInputMask('9999')  # Limite les caractères à des chiffres uniquement
        #self.line_edit.setFixedHeight(50)

        self.unit_label = QLabel(self.unit, self)  
        self.unit_label.setAlignment(Qt.AlignCenter)
        #self.unit_label.setFixedHeight(50)

        # Mettre le QLabel et le QLineEdit dans un QHBoxLayout pour les aligner horizontalement
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.type_label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.unit_label)
        self.setLayout(layout)

    def setText(self, value):
        self.line_edit.setText(value)

    def setFixedWidth(self, w1, w2, w3):
        self.type_label.setFixedWidth(w1)
        self.line_edit.setFixedWidth(w2)
        self.unit_label.setFixedWidth(w3)

    def setReadOnly(self, mybool):
        self.line_edit.setReadOnly(mybool)



class ina219Frame(QFrame):
    def __init__(self, ina219):
        super().__init__()
        self.ina219 = ina219
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("border: 1px solid black;") 
        
        # Voltage
        self.textVoltage = dataMenu("Tension", "V")
        self.textVoltage.setFixedWidth(80,50,15)
        self.textVoltage.setReadOnly(True)

        # Current 
        self.textCurrent = dataMenu("Courant", "mA")
        self.textCurrent.setFixedWidth(80,50,15)
        self.textCurrent.setReadOnly(True)

        # PowerQT
        self.textPower = dataMenu("Puissance", "mW")
        self.textPower.setFixedWidth(80,50,15)
        self.textPower.setReadOnly(True)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.textVoltage)
        layout.addWidget(self.textCurrent)
        layout.addWidget(self.textPower)
        self.setLayout(layout)
        self.setFixedSize(200, 130)

    def update_text_fields(self):
        shunt_voltage = self.ina219.shunt_voltage()
        bus_voltage = self.ina219.voltage()
        current = self.ina219.current()
        power = self.ina219.power()

        # Mettre à jour les champs texte avec des valeurs aléatoires
        self.textVoltage.setText(f"{bus_voltage:+.1f}")
        self.textCurrent.setText(f"{current:+.1f}")
        self.textPower.setText(f"{power:.1f}")

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

        # InaFrame
        self.inaFrame = ina219Frame(self.gpio.get_ina219())
      
        # Layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.TextName)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.inaFrame)
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

    def update_text_fields(self):
        self.inaFrame.update_text_fields()


class DrewControl(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name=name
        self.buttonOn=True
        self.AstraDrew = AstraPwm(name)
        self.initUI()

    def initUI(self):
  
        # Button 
        self.toggle_button = QPushButton(self.name+' Off', self)
        self.set_togglebuttonText()
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_action)

        # Power
        self.textPower = dataMenu("Power", "%")
        self.textPower.setFixedWidth(100,50,15)
        self.textPower.setReadOnly(True)
        
        # Power
        self.textTempConsigne = dataMenu("Consigne", "°C")
        self.textTempConsigne.setFixedWidth(100,50,15)
        self.textTempConsigne.setReadOnly(False)
        self.textTempConsigne.setText("10")

         # InaFrame
        self.inaFrame = ina219Frame(self.AstraDrew.get_ina219())
       

        firstCol = QVBoxLayout()
        firstCol.setSpacing(0)
        firstCol.addWidget(self.toggle_button)        

        # Layout
        secCol = QVBoxLayout()
        secCol.setSpacing(0)
        secCol.addWidget(self.textPower)        
        secCol.addWidget(self.textTempConsigne)        

        thirdCol = QVBoxLayout()
        thirdCol.setSpacing(0)
        thirdCol.addWidget(self.inaFrame)        

        allLayout = QHBoxLayout()
        allLayout.setSpacing(0)
        allLayout.addLayout(firstCol)
        allLayout.addLayout(secCol)
        allLayout.addLayout(thirdCol)
        self.setLayout(allLayout)

    def set_togglebuttonText(self):
        if self.buttonOn:
            self.toggle_button.setText(self.name+' is On Set Off')
            self.toggle_button.setStyleSheet("background-color: green")
        else:
            self.toggle_button.setText(self.name+' is Off Set On')
            self.toggle_button.setStyleSheet("background-color: green")


    def toggle_action(self):
        self.buttonOn = not(self.buttonOn)
        self.set_togglebuttonText()

    def update_text_fields(self):
        ratio=self.AstraDrew.get_ratio()
        self.inaFrame.update_text_fields()
        self.textPower.setText(str(int(ratio)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setSpacing(0)

    widgets = []
    for name in ["AstraDc1", "AstraDc2", "AstraDc3"]:
        wiget=GpioControl(name)
        widgets.append(wiget)
        main_layout.addWidget(wiget)
        
    for name in ["AstraPwm1", "AstraPwm2"]:
        wiget=DrewControl(name)
        widgets.append(wiget)
        main_layout.addWidget(wiget)


    main_window.setLayout(main_layout)
    main_window.setWindowTitle('AstrAlim')
    #main_window.setGeometry(100, 100, 800, 800)
    main_window.show()

    # Créer un timer pour mettre à jour tous les widgets toutes les secondes
    timer = QTimer()
    timer.timeout.connect(lambda: [widget.update_text_fields() for widget in widgets])
    timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
    sys.exit(app.exec_())


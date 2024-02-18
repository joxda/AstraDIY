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
    def __init__(self, unit):
        self.unit=unit
        super().__init__()
        self.initUI()
        self.unit=unit

    def initUI(self):
        self.line_edit = QLineEdit(self)
        #self.line_edit.setInputMask('9999')  # Limite les caractères à des chiffres uniquement
        #self.line_edit.setFixedHeight(50)

        self.unit_label = QLabel(self.unit, self)  
        self.unit_label.setAlignment(Qt.AlignCenter)
        #self.unit_label.setFixedHeight(50)

        # Mettre le QLabel et le QLineEdit dans un QHBoxLayout pour les aligner horizontalement
        layout = QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.unit_label)
        layout.setSpacing(0)
        self.setLayout(layout)

    def setText(self, value):
        self.line_edit.setText(value)

    def setFixedWidth(self, width):
        self.line_edit.setFixedWidth(width)
        self.unit_label.setFixedWidth(width)

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
        self.textVoltage = dataMenu("V")
        self.textVoltage.setFixedWidth(50)
        self.textVoltage.setReadOnly(True)

        # Current 
        self.textCurrent = dataMenu("mA")
        self.textCurrent.setFixedWidth(50)
        self.textCurrent.setReadOnly(True)

        # PowerQT
        self.textPower = dataMenu("mW")
        self.textPower.setFixedWidth(50)
        self.textPower.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.textVoltage)
        layout.addWidget(self.textCurrent)
        layout.addWidget(self.textPower)
        layout.setSpacing(1)
        self.setLayout(layout)
        self.setFixedSize(120, 130)

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
        self.setStyleSheet("border: 1px solid black;") 
        
        # Zone de texte initiale
        self.TextName = QLabel(self.name, self)
        #self.TextName.setReadOnly(True)
        self.TextName.setFixedWidth(100)

        # Bouton On/Off
        self.toggle_button = QPushButton('Off set On', self)
        self.toggle_button.setFixedWidth(150)
        self.toggle_button.setStyleSheet("border: 1px solid black;") 
        self.set_togglebuttonText()
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_action)

        # InaFrame
        self.inaFrame = ina219Frame(self.gpio.get_ina219())
      
        # Layout
        layout = QHBoxLayout()
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
        self.textPower = dataMenu("%")
        self.textPower.setFixedWidth(60)
        self.textPower.setReadOnly(True)
        
        # Power
        self.textTempConsigne = dataMenu("°C")
        self.textTempConsigne.setFixedWidth(30)
        self.textTempConsigne.setReadOnly(False)
        self.textTempConsigne.setText("10")
         # InaFrame
        self.inaFrame = ina219Frame(self.AstraDrew.get_ina219())
       
        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.toggle_button)        
        layout.addWidget(self.textPower)        
        layout.addWidget(self.textTempConsigne)        
        layout.addWidget(self.inaFrame)
        self.setLayout(layout)

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

    # Ajouter un widget de titre
    title_widget = QLabel("Widgets avec bouton On/Off et zones de texte")
    main_layout.addWidget(title_widget)

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
    main_window.setWindowTitle('Widgets avec bouton On/Off et zones de texte')
    main_window.setGeometry(100, 100, 700, 200)
    main_window.show()

    # Créer un timer pour mettre à jour tous les widgets toutes les secondes
    timer = QTimer()
    timer.timeout.connect(lambda: [widget.update_text_fields() for widget in widgets])
    timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
    sys.exit(app.exec_())


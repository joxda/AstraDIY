#!/bin/env python3
import sys
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from ina219 import INA219
from AstraGpio import AstraGpio  


class GpioControl(QWidget):
    def __init__(self, name, ina219, pin):
        super().__init__()
        self.name=name
        self.ina219=ina219
        self.gpio = AstraGpio(pin)
        self.initUI()

    def initUI(self):
        # Zone de texte initiale
        self.initial_text = QLineEdit(self.name, self)
        self.initial_text.setReadOnly(True)

        # Bouton On/Off
        self.toggle_button = QPushButton('Off', self)
        self.set_togglebuttonText()
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_action)

        # Zones de texte
        self.text_edit1 = QLineEdit(self)
        self.text_edit2 = QLineEdit(self)
        self.text_edit3 = QLineEdit(self)

        # Définir une largeur fixe pour les zones de texte
        self.initial_text.setFixedWidth(200)
        self.text_edit1.setFixedWidth(200)
        self.text_edit2.setFixedWidth(200)
        self.text_edit3.setFixedWidth(200)
        
        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.initial_text)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.text_edit1)
        layout.addWidget(self.text_edit2)
        layout.addWidget(self.text_edit3)
        self.setLayout(layout)

    def set_togglebuttonText(self):
        if self.gpio.is_on():
            self.toggle_button.setText('Set Off')
        else:
            self.toggle_button.setText('Set On')


    def toggle_action(self):
        self.gpio.switch_onoff()
        self.set_togglebuttonText()
        self.gpio.print_status()

    def update_text_fields(self):
        shunt_voltage = self.ina219.shunt_voltage()
        bus_voltage = self.ina219.voltage()
        current = self.ina219.current()
        power = self.ina219.power()

        # Mettre à jour les champs texte avec des valeurs aléatoires
        self.text_edit1.setText(f"Bus {bus_voltage:+.1f}V")
        self.text_edit2.setText(f"Current: {current:+.1f}mA")
        self.text_edit3.setText(f"{power:.1f}mW")


if __name__ == '__main__':
    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    ina219_set = {
            "alim_1_i2c_41   ": {"address": 0x41, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 37},
            "alim_2_i2c_44   ": {"address": 0x44, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 38},
            "alim_3_i2c_45_5V": {"address": 0x46, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 40},
            #"alim_4_i2c_47   ": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6},
            #"alim_5_i2c_47   ": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6}
    }


    app = QApplication(sys.argv)
    main_window = QWidget()
    main_layout = QVBoxLayout()

    # Ajouter un widget de titre
    title_widget = QLabel("Widgets avec bouton On/Off et zones de texte")
    main_layout.addWidget(title_widget)

    widgets = []
    for name, info in ina219_set.items():
        address = info["address"]
        shunt_ohms = info["shunt_ohms"]
        max_expected_amps = info["max_expected_amps"]
        max_expected_amps = info["max_expected_amps"]
        ina219_set[name]["ina219_object"] = INA219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
        ina219_set[name]["ina219_object"].configure()
        ina219_set[name]["ina219_wiget"]=GpioControl(name,ina219_set[name]["ina219_object"], pin=ina219_set[name]["pin"])
        widgets.append(ina219_set[name]["ina219_wiget"])
        main_layout.addWidget(ina219_set[name]["ina219_wiget"])


    main_window.setLayout(main_layout)
    main_window.setWindowTitle('Widgets avec bouton On/Off et zones de texte')
    main_window.setGeometry(100, 100, 700, 200)
    main_window.show()

    # Créer un timer pour mettre à jour tous les widgets toutes les secondes
    timer = QTimer()
    timer.timeout.connect(lambda: [widget.update_text_fields() for widget in widgets])
    timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
    sys.exit(app.exec_())


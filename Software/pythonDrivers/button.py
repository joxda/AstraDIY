#!/bin/env python3
import sys
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from ina219 import INA219
from AstraGpio import AstraGpio


class GpioControl(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name=name
        self.gpio = AstraGpio(name)
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
        shunt_voltage = self.gpio.shunt_voltage()
        bus_voltage = self.gpio.voltage()
        current = self.gpio.current()
        power = self.gpio.power()

        # Mettre à jour les champs texte avec des valeurs aléatoires
        self.text_edit1.setText(f"Bus {bus_voltage:+.1f}V")
        self.text_edit2.setText(f"Current: {current:+.1f}mA")
        self.text_edit3.setText(f"{power:.1f}mW")


if __name__ == '__main__':
    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    #"alim_4_i2c_47   ": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6},
    #"alim_5_i2c_47   ": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6}


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


    main_window.setLayout(main_layout)
    main_window.setWindowTitle('Widgets avec bouton On/Off et zones de texte')
    main_window.setGeometry(100, 100, 700, 200)
    main_window.show()

    # Créer un timer pour mettre à jour tous les widgets toutes les secondes
    timer = QTimer()
    timer.timeout.connect(lambda: [widget.update_text_fields() for widget in widgets])
    timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
    sys.exit(app.exec_())


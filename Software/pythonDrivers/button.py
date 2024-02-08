#!/bin/env python3
import sys
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from ina219 import INA219


class TriggerManager:
    def __init__(self):
        self.triggered = False

    def set_triggered(self, state):
        self.triggered = state

    def is_triggered(self):
        return self.triggered


class Widget(QWidget):
    def __init__(self, name, ina219):
        super().__init__()
        self.name=name
        self.ina219=ina219
        self.initUI()

    def initUI(self):
        # Zone de texte initiale
        self.initial_text = QLineEdit(self.name, self)
        self.initial_text.setReadOnly(True)

        # Bouton On/Off
        self.toggle_button = QPushButton('Off', self)
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

    def toggle_action(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText('On')
            # Code à exécuter lorsque le bouton est activé
            print("Le bouton est activé.")
        else:
            self.toggle_button.setText('Off')
            # Code à exécuter lorsque le bouton est désactivé
            print("Le bouton est désactivé.")

    def update_text_fields(self):
        shunt_voltage = self.ina219.shunt_voltage()
        bus_voltage = self.ina219.voltage()
        current = self.ina219.current()
        power = self.ina219.power()

        # Mettre à jour les champs texte avec des valeurs aléatoires
        self.text_edit1.setText(f"Bus {bus_voltage:+.3f}V")
        self.text_edit2.setText(f"Current: {current:+.3f}A")
        self.text_edit3.setText(f"{power:.3f}mW")


if __name__ == '__main__':
    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    ina219_set = {
            "alim_1_i2c_41   ": {"address": 0x41, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 37, "gpio": 26},
        "alim_2_i2c_44   ": {"address": 0x44, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 38, "gpio": 20},
        "alim_3_i2c_45_5V": {"address": 0x46, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 40, "gpio": 21},
        #"alim_4_i2c_47   ": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6},
        #"alim_5_i2c_47   ": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6}
    }


    app = QApplication(sys.argv)
    trigger_manager = TriggerManager()
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
        ina219_set[name]["ina219_wiget"]=Widget(name,ina219_set[name]["ina219_object"])
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
    trigger_manager.set_triggered(True)
    sys.exit(app.exec_())


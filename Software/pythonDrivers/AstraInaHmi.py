#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt
from AstraIna import powerIna219



class dataMenu(QWidget):
    def __init__(self, label, unit):
        self.unit=unit
        self.label=label
        super().__init__()
        self.initUI()

    def initUI(self):
        self.type_label = QLabel(self.label, self)  
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.adjustSize()
        #self.type_label.setFixedHeight(50)

        self.line_edit = QLineEdit(self)
        self.line_edit.adjustSize()
        #self.line_edit.setInputMask('9999')  # Limite les caractères à des chiffres uniquement
        #self.line_edit.setFixedHeight(50)

        self.unit_label = QLabel(self.unit, self)  
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.unit_label.adjustSize()
        
        #self.unit_label.setFixedHeight(50)

        # Mettre le QLabel et le QLineEdit dans un QHBoxLayout pour les aligner horizontalement
        layout = QHBoxLayout()
        layout.addWidget(self.type_label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.unit_label)
        layout.setSpacing(0)
        layout.setContentsMargins(1, 1, 1, 1)  # Set the margins inside the frame
        self.setLayout(layout)
        self.adjustSize()
        

    def setText(self, value):
        self.line_edit.setText(value)

    def setInputMask(self, value):
        self.line_edit.setInputMask(value)

    def getText(self):
        return self.line_edit.text()

    def setFixedWidth(self, w1, w2, w3):
        self.type_label.setFixedWidth(w1)
        self.line_edit.setFixedWidth(w2)
        self.unit_label.setFixedWidth(w3)
        pass

    def setReadOnly(self, mybool):
        self.line_edit.setReadOnly(mybool)

    def connect(self, doSomething):
        self.line_edit.textEdited.connect(doSomething)


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

        for name in powerIna219.getListNames():
            wiget=ina219Frame(powerIna219(name=name))
            self.widgets.append(wiget)
            self.main_layout.addWidget(wiget)
        
        self.setLayout(self.main_layout)
        self.setWindowTitle('AstrAlim')


        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [widget.update_text_fields() for widget in self.widgets])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def closeEvent(self, event):
        powerIna219.exitAll()
        #os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()


    sys.exit(app.exec_())


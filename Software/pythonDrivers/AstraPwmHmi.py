#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt
from AstraPwm import AstraPwm
from AstraDataMenu import dataMenu


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
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_action)

        self.save_button = QPushButton('Save', self)
        self.save_button.setCheckable(True)
        self.save_button.clicked.connect(self.AstraDrew.save)


        # Selection capteur temperature
        self.selTemp = QComboBox(self)        
        curtempname = self.AstraDrew. get_associateTemp()
        defaultIndex=0
        curindex=0
        for tempId in self.AstraDrew.get_listTemp():
            self.selTemp.addItem(tempId)
            if tempId == curtempname:
                defaultIndex=curindex
            curindex=curindex+1
        self.selTemp.setCurrentIndex(defaultIndex)
        #self.set_associateTemp(0)
        self.selTemp.currentIndexChanged.connect(self.set_associateTemp)

        # Power
        self.textPower = dataMenu("Power", "%")
        self.textPower.setFixedWidth(100,70,15)
        self.textPower.setReadOnly(False)
        #self.textPower.setInputMask("000")
        self.textPower.connect(self.set_power)

        # Temp consigne
        self.textTempConsigne = dataMenu("Consigne", "°C")
        self.textTempConsigne.setFixedWidth(100,70,15)
        self.textTempConsigne.setReadOnly(False)
        self.textTempConsigne.connect(self.set_cmdtemp)

        # Measure Temp
        self.textTempMesure = dataMenu("Measure", "°C")
        self.textTempMesure.setFixedWidth(100,70,15)
        self.textTempMesure.setReadOnly(True)

        # Set defauls
        self.set_buttonOff()
        self.set_togglebuttonText()
        self.textTempMesure.setText("10")
        self.textTempConsigne.setText("10")

        firstCol = QVBoxLayout()
        firstCol.setSpacing(0)
        firstCol.addWidget(self.toggle_button)        
        firstCol.addWidget(self.selTemp)        
        firstCol.addWidget(self.save_button)        

        # Layout
        secCol = QVBoxLayout()
        secCol.setSpacing(0)
        secCol.addWidget(self.textPower)        
        secCol.addWidget(self.textTempConsigne)
        secCol.addWidget(self.textTempMesure)        

        allLayout = QHBoxLayout()
        allLayout.setSpacing(0)
        allLayout.addLayout(firstCol)
        allLayout.addLayout(secCol)
        self.setLayout(allLayout)

    def set_textPowerReadOnly(self, val):
        self.textPower.setReadOnly(val)

    def set_togglebuttonText(self):
        if self.buttonOn:
            self.toggle_button.setText("auto "+self.name+' is On Set Off')
            self.toggle_button.setStyleSheet("background-color: #f75457; border: 1px solid black;")
            self.AstraDrew.startAserv()
        else:
            self.toggle_button.setText("auto "+self.name+' is Off Set On')
            self.toggle_button.setStyleSheet("background-color: #3cbaa2; border: 1px solid black;")
            if self.AstraDrew.isAserv():
                self.AstraDrew.stopAserv()
                self.AstraDrew.set_ratio(0)
            self.textPower.setText(str(self.AstraDrew.get_ratio()))

    def set_associateTemp(self, index):
        selected_item_text = self.selTemp.itemText(index)
        self.AstraDrew.set_associateTemp(selected_item_text)
        #print("Selected Temp Sensor:", selected_item_text)

    def set_power(self):
        ratio=self.textPower.getText()
        try:
            ratio=int(ratio)
        except:
            pass
        else:
            #print("self.AstraDrew.set_ratio(",ratio,")")
            self.AstraDrew.set_ratio(ratio)
            self.set_buttonOff()

    def set_cmdtemp(self):
        self.AstraDrew.set_cmdTemp(self.textTempConsigne.getText())

    def toggle_action(self):
        self.buttonOn = not(self.buttonOn)
        self.set_togglebuttonText()

    def set_buttonOff(self):
        self.buttonOn = False
        self.set_togglebuttonText()

    def update_text_fields(self):
        if self.buttonOn:
            ratio=self.AstraDrew.get_ratio()
            self.textPower.setText(f"{ratio:.1f}")
            self.textPower.setReadOnly(True)
        else:
            self.textPower.setReadOnly(False)
        temp=self.AstraDrew.get_temp()
        self.textTempMesure.setText(f"{temp:+.1f}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)

        self.widgets = []
        for name in ["AstraPwm1", "AstraPwm2"]:
            wiget=DrewControl(name)
            self.widgets.append(wiget)
            self.main_layout.addWidget(wiget)


        self.setLayout(self.main_layout)
        self.setWindowTitle('AstrAlim')


        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [widget.update_text_fields() for widget in self.widgets])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def closeEvent(self, event):
        os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()


    sys.exit(app.exec_())


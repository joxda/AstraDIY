#!/bin/env python3
import sys
import math
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import  QLabel, QFrame
from PyQt5.QtCore import Qt
from AstraGps import AstraGps
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



class MainGpsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gps:AstraGps = AstraGps()
        # Layout de type grille
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(0)

        # Add QLabel at the top
        self.gpsSyncState:dataMenu = dataMenu(" GpsSyncState = ", " ", parent=self)
        self.gpsSyncState.setReadOnly(True)
        self.gpsSyncState.setStyleSheet("border: 1px solid black;") 

        self.gpsLastTime:dataMenu = dataMenu(f" Time = ", " ", parent=self)
        self.gpsLastTime.setReadOnly(True)
        self.gpsLastTime.setStyleSheet("border: 1px solid black;") 

        self.gpsPPSCount:dataMenu = dataMenu(f" PPS Count = ", " ", parent=self)
        self.gpsPPSCount.setReadOnly(True)
        self.gpsPPSCount.setStyleSheet("border: 1px solid black;") 

        self.main_layout.addWidget(self.gpsSyncState, 0, 0)
        self.main_layout.addWidget(self.gpsLastTime, 0, 1)
        self.main_layout.addWidget(self.gpsPPSCount, 0, 2)
         
        self.setLayout(self.main_layout)
        self.setWindowTitle('Gps')

        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [self.update_text_fields()])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def  update_text_fields(self):
        self.gpsSyncState.setText(self.gps.gpsSyncState())
        self.gpsLastTime.setText(self.gps.gpsTimeStamp())
        self.gpsPPSCount.setText(self.gps.gpsCountPPS())
  

    def closeEvent(self, event):
        self.gps.exitAll()
        #os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainGpsWindow()
    main_window.show()


    sys.exit(app.exec_())


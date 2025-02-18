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
        self.gps:AstraGps = AstraGps().get_instance()
        # Layout de type grille
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(0)

        # Add QLabel at the top
        self.gpsLabel = QLabel("Gps", self)  
        self.gpsLabel.setAlignment(Qt.AlignCenter)
        self.gpsLabel.adjustSize()
        self.gpsLabel.setFixedHeight(40)

        self.gpsSyncState:dataMenu = dataMenu(" GpsSyncState = ", " ", parent=self)
        self.gpsSyncState.setReadOnly(True)
        self.gpsSyncState.setStyleSheet("border: 1px solid black;") 

        self.gpsLastTime:dataMenu = dataMenu(f" Time = ", " ", parent=self)
        self.gpsLastTime.setReadOnly(True)
        self.gpsLastTime.setStyleSheet("border: 1px solid black;") 

        self.gpsPPSCount:dataMenu = dataMenu(f" PPS Count = ", " ", parent=self)
        self.gpsPPSCount.setReadOnly(True)
        self.gpsPPSCount.setStyleSheet("border: 1px solid black;") 

        self.gpsLatitude:dataMenu = dataMenu(f"Lat.= ", "°", parent=self)
        self.gpsLatitude.setReadOnly(True)
        self.gpsLatitude.setStyleSheet("border: 1px solid black;") 

        self.gpsLongitude:dataMenu = dataMenu(f"Long.= ", "°", parent=self)
        self.gpsLongitude.setReadOnly(True)
        self.gpsLongitude.setStyleSheet("border: 1px solid black;") 

        self.gpsAlt:dataMenu = dataMenu(f"Alt.= ", "m", parent=self)
        self.gpsAlt.setReadOnly(True)
        self.gpsAlt.setStyleSheet("border: 1px solid black;")         

        self.main_layout.addWidget(self.gpsLabel, 0, 0)
        self.main_layout.addWidget(self.gpsSyncState, 1, 0)
        self.main_layout.addWidget(self.gpsPPSCount, 1, 1)
        self.main_layout.addWidget(self.gpsLastTime, 2, 0, 1, 2)
        self.main_layout.addWidget(self.gpsLatitude, 3, 0)
        self.main_layout.addWidget(self.gpsLongitude, 3, 1)
        self.main_layout.addWidget(self.gpsAlt, 3, 2)
        
        self.ntpLabel = QLabel("Ntp", self)  
        self.ntpLabel.setAlignment(Qt.AlignCenter)
        self.ntpLabel.adjustSize()
        self.ntpLabel.setFixedHeight(40)

        self.ntpTime:dataMenu = dataMenu(f"Ntp Time = ", " ", parent=self)
        self.ntpTime.setReadOnly(True)
        self.ntpTime.setStyleSheet("border: 1px solid black;") 

        self.ntpprecision:dataMenu = dataMenu(f"SystemTime Precision = +/-", "uS", parent=self)
        self.ntpprecision.setReadOnly(True)
        self.ntpprecision.setStyleSheet("border: 1px solid black;") 

        self.main_layout.addWidget(self.ntpLabel, 4, 0, 1, 3)
        self.main_layout.addWidget(self.ntpTime, 5, 0, 1, 2)
        self.main_layout.addWidget(self.ntpprecision, 6, 0, 1, 2)

        self.setLayout(self.main_layout)
        self.setWindowTitle('Gps')

        # Créer un timer pour mettre à jour tous les widgets toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: [self.update_text_fields()])
        self.timer.start(1000)  # Met à jour toutes les 1000 millisecondes (1 seconde)
 
    def  update_text_fields(self):
        self.gpsSyncState.setText(f"{self.gps.gpsSyncState()}D")
        self.gpsLastTime.setText(f"{self.gps.gpsTimeStamp()}")
        self.gpsPPSCount.setText(f"{self.gps.gpsCountPPS()}")
        lat, long, alt = self.gps.gpsGetPosition()
        self.gpsLatitude.setText(f"{lat}")
        self.gpsLongitude.setText(f"{long}")
        self.gpsAlt.setText(f"{alt}")
        self.ntpTime.setText(f"{self.gps.ntpTimeStampS()}")
        self.ntpprecision.setText(f"{self.gps.ntpTimePrecisionUs()}")

  

    def closeEvent(self, event):
        self.gps.exitAll()
        #os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainGpsWindow()
    main_window.show()


    sys.exit(app.exec_())


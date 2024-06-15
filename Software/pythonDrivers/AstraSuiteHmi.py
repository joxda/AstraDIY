#!/bin/env python3
import sys
import os
import signal
from AstraGpioHmi import MainGpioWindow
from AstraPwmHmi import MainPwmWindow
from AstraInaHmi import MainInaWindow

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel


# Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QTabWidget
        self.tabs = QTabWidget()
        
        # Create instances of the widgets
        self.pwm_hmi = MainPwmWindow()
        self.gpio_hmi = MainGpioWindow(size=60)
        self.ina_hmi = MainInaWindow()
        
        # Add widgets as tabs
        self.tabs.addTab(self.pwm_hmi, "PwmH")
        self.tabs.addTab(self.gpio_hmi, "Gpio")
        self.tabs.addTab(self.ina_hmi, "Ina")
        
        # Set the central widget of the main window to be the QTabWidget
        self.setCentralWidget(self.tabs)
        
        # Window settings
        self.setWindowTitle('Astra HMI')
        self.resize(400, 300)

    def closeEvent(self, event):
        os.kill(os.getpid(), signal.SIGTERM)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

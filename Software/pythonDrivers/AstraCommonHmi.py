#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect



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
        self.type_label.setFixedHeight(50)

        self.line_edit = QLineEdit(self)
        self.line_edit.adjustSize()
        #self.line_edit.setInputMask('9999')  # Limite les caractères à des chiffres uniquement
        self.line_edit.setFixedHeight(50)

        self.unit_label = QLabel(self.unit, self)  
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.type_label.setFixedHeight(50)
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

class AnimatedToggleButton(QWidget):
    def __init__(self, parent=None, initial_state=False):
        super().__init__(parent)
        self.setFixedSize(100, 50)

        # Background
        self.background = QPushButton('', self)
        self.background.setFixedSize(100, 50)
        self.background.setStyleSheet("background-color: lightgray; border-radius: 25px;")
        self.background.setEnabled(False)

        # Slider
        self.slider = QPushButton('', self)
        self.slider.setFixedSize(50, 50)
        self.slider.setStyleSheet("background-color: white; border-radius: 25px;")
        self.slider.setCheckable(True)
        self.slider.setChecked(initial_state)
        self.slider.clicked.connect(self.toggle)

        # Animation
        self.animation = QPropertyAnimation(self.slider, b"geometry")
        self.animation.setDuration(250)  # Duration of the animation in milliseconds

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.background)
        layout.addWidget(self.slider)

        # Set initial state
        self.set_initial_state(initial_state)

    def set_initial_state(self, state):
        if state:
            self.slider.setGeometry(QRect(50, 0, 50, 50))
            self.background.setStyleSheet("background-color: green; border-radius: 25px;")
            self.slider.setText('On')
        else:
            self.slider.setGeometry(QRect(0, 0, 50, 50))
            self.background.setStyleSheet("background-color: red; border-radius: 25px;")
            self.slider.setText('Off')

    def toggle(self):
        if self.slider.isChecked():
            self.animation.setStartValue(QRect(0, 0, 50, 50))
            self.animation.setEndValue(QRect(50, 0, 50, 50))
            self.background.setStyleSheet("background-color: green; border-radius: 25px;")
            self.slider.setText('On')
        else:
            self.animation.setStartValue(QRect(50, 0, 50, 50))
            self.animation.setEndValue(QRect(0, 0, 50, 50))
            self.background.setStyleSheet("background-color: red; border-radius: 25px;")
            self.slider.setText('Off')
        self.animation.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    
    # Création du bouton de bascule animé avec un état initial
    animated_toggle_button = AnimatedToggleButton(window, initial_state=True)
    data_menu = dataMenu('toto', 'ms')
    
    # Layout
    layout = QVBoxLayout()
    layout.addWidget(animated_toggle_button)
    layout.addWidget(data_menu)
    window.setLayout(layout)
    
    # Configuration de la fenêtre principale
    window.setWindowTitle('Animated Toggle Button and data menue')
    window.resize(200, 100)
    window.show()
    
    sys.exit(app.exec_())


#!/bin/env python3
import sys
import os
import signal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect



class dataMenu(QWidget):
    def __init__(self, label, unit, parent=None):
        super().__init__(parent)
        self.unit=unit
        self.label=label

        self.type_label = QLabel(self.label, self)  
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.adjustSize()
        self.type_label.setFixedHeight(50)

        self.line_edit = QLineEdit(self)
        self.line_edit.adjustSize()
        #self.line_edit.setInputMask('9999')  # Limite les caractères à des chiffres uniquement
        self.line_edit.setFixedHeight(50)
        self.line_edit.setAlignment(Qt.AlignRight)

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

        # Frame pour les assembler
        self.subWindow = QFrame()
        self.subWindow.setFrameShape(QFrame.Box)
        self.subWindow.setFrameShadow(QFrame.Raised)
        self.subWindow.setLayout(layout)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.subWindow)
        self.setLayout(mainLayout)
        self.adjustSize()
        self.setStyleSheet("""
                QLineEdit {
                    border: 1px solid black;
                }
            """)
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
        if mybool:
            #self.setStyleSheet("background-color: #3cbaa2; border: 1px solid black;")
            self.setStyleSheet("""
                QLineEdit {
                    background: transparent;
                    color: black;
                }
            """)
        else:
            self.setStyleSheet("""
                QLineEdit {
                    border: 1px solid black;
                }
            """)

    def connect(self, doSomething):
        self.line_edit.textEdited.connect(doSomething)

class AnimatedToggleButton(QWidget):
    def __init__(self, parent=None, initial_state=False, toggle_callback=None, size=30):
        super().__init__(parent)
        self.size=size
        self.radius=str(int(size/2))
        self.setFixedSize(self.size*2, self.size)
        self.toggle_callback = None
        
        # Background
        self.background = QPushButton('', self)
        self.background.setFixedSize(self.size*2, self.size)
        self.background.setStyleSheet("background-color: lightgray; border-radius: "+self.radius+"px;")
        self.background.setCheckable(True)
        self.background.setChecked(initial_state)
        self.background.clicked.connect(self.toggle)
        
        # Slider
        self.slider = QPushButton('', self)
        self.slider.setFixedSize(self.size, self.size)
        self.slider.setStyleSheet("background-color: white; border-radius: "+self.radius+"px;")
        self.slider.setEnabled(True)
        self.slider.clicked.connect(self.toggle_bis)

        # Animation
        self.animation = QPropertyAnimation(self.slider, b"geometry")
        self.animation.setDuration(250)  # Duration of the animation in milliseconds

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.background)
        layout.addWidget(self.slider)

        # Set initial state
        self.slider.setChecked(initial_state)
        self.toggle(initial_state)
        self.toggle_callback = toggle_callback  # Save the callback function


    def toggle_bis(self):
        current_state = self.background.isChecked()
        self.background.setChecked(not current_state)
        self.toggle(not current_state)
        
    def toggle(self):
        self.update(self.background.isChecked())
        
    def toggle(self, state):
        if self.background.isChecked():
            self.animation.setStartValue(QRect(0, 0, self.size, self.size))
            self.animation.setEndValue(QRect(self.size, 0, self.size, self.size))
            self.background.setStyleSheet("background-color: green; border-radius: "+self.radius+"px;")
            self.slider.setText('On')
        else:
            self.animation.setStartValue(QRect(self.size, 0, self.size, self.size))
            self.animation.setEndValue(QRect(0, 0, self.size, self.size))
            self.background.setStyleSheet("background-color: red; border-radius: "+self.radius+"px;")
            self.slider.setText('Off')
        self.animation.start()

        # Call the callback function if provided
        if self.toggle_callback:
            self.toggle_callback(self.background.isChecked())
            
    def isChecked(self):
        return self.background.isChecked()

    def setState(self, state):
        self.update(state)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()

    data_menu = dataMenu('toto', 'ms')
    data_menu.setText("tutu")
    rodata_menu = dataMenu('toto', 'ms')
    rodata_menu.setReadOnly(True)
    rodata_menu.setText("ReadOnly")
    
    def on_toggle(state):
        print(f'Toggle state changed to: {"On" if state else "Off"}')
        rodata_menu.setReadOnly(state)
        

 
    # Création du bouton de bascule animé avec un état initial
    animated_toggle_button1 = AnimatedToggleButton(window, initial_state=False, toggle_callback=on_toggle)
    animated_toggle_button2 = AnimatedToggleButton(window, initial_state=True, toggle_callback=on_toggle)

    # Layout
    layout = QVBoxLayout()
    layout.addWidget(animated_toggle_button1)
    layout.addWidget(animated_toggle_button2)
    layout.addWidget(data_menu)
    layout.addWidget(rodata_menu)
    window.setLayout(layout)

    

       
    # Configuration de la fenêtre principale
    window.setWindowTitle('Animated Toggle Button and data menue')
    window.resize(200, 100)
    window.show()
    
    sys.exit(app.exec_())


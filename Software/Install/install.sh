#!/bin/env bash

sudo apt -y install gpsd chrony

sudo apt-get -y install git
sudo apt-get -y install python3-smbus  python3 python3-pip python3-testresources python3-setuptools python3-ipython ipython3 

# Librairie gpiod
sudo apt-get -y install python3-libgpiod
# outils pour debug
sudo apt -y install gpiod

# i2c 
i2cdetect  -y 1



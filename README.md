# AstraDIY
# Description :
This project is a documentation, Software Repository and archiving space for projects :
   * [AstrAlim](https://oshwlab.com/pololamag/astralim)
   * [AstrOnStep](https://oshwlab.com/pololamag/astronstep)
   * [HEMY](https://github.com/polvinc/HEMY)
   * TeenAstro-Redux
   * HEMY Break Driver
The main documentation is in the [associated wiki](https://github.com/dgedgedge/AstraDIY/wiki/WhatIsAstraDIY)
The spcific Software documentation are in the the sub directories of this project.

It contains :
   * the saved element for the hardware projet. See Hadrware directory.
   * Software developped scripts to simplify usage of the hardware. See Software diretory.

# Installation :
## Gps :
See [Installation process](Software/Install/README.md)
## Software Python Drivers:
### Manipulating GPIO :
   * AstraGpio.py
   * AstraGpioHmi.py
### Manage DrewHeater :
   * AstraPwm.py
   * AstraPwmHmi.py
### Monitoring Power consumption :
   * AstraIna.py
   * AstraInaHmi.py
## Usage with kstars/Indi:
## Licences :
   * The current softwares are provided under the following [LICENSE](LICENSE)
   * Save for the following where the  authors either have not express the Licence and/or distributed with a similar licence :
      * The script included bme_lib.py is a 2024 copy of [bme280.py](https://github.com/awitwicki/MMM-BME280/blob/master/bme280.py) we are using as is.
      * The script ina219.py is a 2024 copy of [ina219.py](https://github.com/chrisb2/pi_ina219/blob/master/ina219.py) where we did modifiy the I2c access to be compatible with latest kernel and PI5.
      * The script syspwm.py is a 2024 copy of [syspwm.py](https://github.com/jdimpson/syspwm/blob/master/syspwm.py) where we did adapt to paths specific to PI5.


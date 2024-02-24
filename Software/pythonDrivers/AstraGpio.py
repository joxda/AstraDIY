#!/bin/env python3
# GPIO used PA17

import gpiod
from powerIna219 import powerIna219

import time

astraGpioSet = { 
                "AstraDc1": {"address": 0x41, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 37},
                "AstraDc2": {"address": 0x44, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 38},
                "AstraDc3": {"address": 0x46, "shunt_ohms": 0.02, "max_expected_amps": 6, "pin": 40},
}
pin2gpio = { 37:26, 38:20, 40:21}

class AstraGpio():
    def __init__(self, name):
        self.name = name
        self.inacaract={}
        if name in astraGpioSet :
            self.inacaract=astraGpioSet[self.name]
        else:
            raise Exception("Unkown AstraGpi")
        address = self.inacaract["address"]
        shunt_ohms = self.inacaract["shunt_ohms"]
        max_expected_amps = self.inacaract["max_expected_amps"]
        max_expected_amps = self.inacaract["max_expected_amps"]
         
        self.ina219=powerIna219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
        pin=self.inacaract["pin"]
        self.gpioline = gpiod.find_line(f"PIN{pin:d}")
        if self.gpioline == None: 
            self.gpioline = gpiod.find_line(f"PIN{pin:d}")
        if self.gpioline == None: 
            self.gpioline = gpiod.find_line(f"GPIO{pin2gpio[pin]:d}")
        if self.gpioline == None: 
            self.gpioline = gpiod.find_line(f"GPIO{pin2gpio[pin]:d}")
        if self.gpioline == None:
            raise Exception("Gpio Not Found")
        #self.gpioline.request(consumer='AstrAlim', type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        self.gpioline.request(consumer='AstrAlim')
        if self.gpioline.direction() != self.gpioline.DIRECTION_OUTPUT:
            print("Set dirout at init")
            self.gpioline.set_direction_output()
        self.ina219.configure()

    def get_ina219(self):
        return self.ina219

    def print_status(self):
        print(self.name,":",self.gpioline.name(), ":", self.gpioline.get_value(), "=>", self.ina219.voltage(), "V", self.ina219.current(), "mA")

    def get_name(self):
        return self.gpioline.name()

    def switch_onoff(self):
        if self.gpioline.get_value() == 0:
            self.gpioline.set_value(1)
        else:
            self.gpioline.set_value(0)

    def is_on(self):
        return (self.gpioline.get_value() != 0)


if __name__ == "__main__":
    listastragpio = []
    for name in  [ "AstraDc1", "AstraDc2", "AstraDc3" ]:
        listastragpio.append(AstraGpio(name))
    while True:
        for line in listastragpio:
            line.switch_onoff()
            time.sleep(1)
            line.print_status()



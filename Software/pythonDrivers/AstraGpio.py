#!/bin/env python3
# GPIO used PA17

import gpiod
import time


class AstraGpio():
    astraGpioSet = { 
                "AstraDc1": {"pin": 37},
                "AstraDc2": {"pin": 38},
                "AstraDc3": {"pin": 40},
    }
    pin2gpio = { 37:26, 38:20, 40:21}
    def __init__(self, name):
        self.name = name
        if name in self.astraGpioSet :
            self.inacaract=self.astraGpioSet[self.name]
        else:
            raise Exception("Unkown AstraGpi")
         
        pin=self.inacaract["pin"]
        self.gpioline = gpiod.find_line(f"PIN{pin:d}")
        if self.gpioline == None: 
            self.gpioline = gpiod.find_line(f"PIN{pin:d}")
        if self.gpioline == None: 
            self.gpioline = gpiod.find_line(f"GPIO{self.pin2gpio[pin]:d}")
        if self.gpioline == None: 
            self.gpioline = gpiod.find_line(f"GPIO{self.pin2gpio[pin]:d}")
        if self.gpioline == None:
            raise Exception("Gpio Not Found")
        #self.gpioline.request(consumer='AstrAlim', type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        self.gpioline.request(consumer='AstrAlim')
        if self.gpioline.direction() != self.gpioline.DIRECTION_OUTPUT:
            print("Set dirout at init")
            self.gpioline.set_direction_output()

    def print_status(self):
        print(self.name,":",self.gpioline.name(), ":", self.gpioline.get_value())

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



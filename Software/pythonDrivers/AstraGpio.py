#!/bin/env python3
# GPIO used PA17

import gpiod
import time
class AstraGpio:
    def __init__(self, pin): 
        pin2gpio = { 37:26, 38:20, 40:21}
        self.line = gpiod.find_line(f"PIN{pin:d}")
        if self.line == None: 
            self.line = gpiod.find_line(f"PIN{pin:d}")
        if self.line == None: 
            self.line = gpiod.find_line(f"GPIO{pin2gpio[pin]:d}")
        if self.line == None: 
            self.line = gpiod.find_line(f"GPIO{pin2gpio[pin]:d}")
        if self.line == None:
            raise GpioNotFofoobarund
        #self.line.request(consumer='AstrAlim', type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        self.line.request(consumer='AstrAlim')
        if self.line.direction() != self.line.DIRECTION_OUTPUT:
            print("Set dirout at init")
            self.line.set_direction_output()


    def print_status(self):
        print(self.line.name(), ":", self.line.get_value())

    def get_name(self):
        return self.line.name()

    def switch_onoff(self):
        if self.line.get_value() == 0:
            self.line.set_value(1)
        else:
            self.line.set_value(0)

    def is_on(self):
        return (self.line.get_value() != 0)


if __name__ == "__main__":
    listastragpio = []
    for pin in  [ 37, 38, 40 ]:
        listastragpio.append(AstraGpio(pin))
    while True:
        for line in listastragpio:
            line.switch_onoff()
            line.print_status()
        time.sleep(1)



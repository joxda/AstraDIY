#!/bin/env python3
# GPIO used PA17

from ina219 import INA219
from syspwm import SysPWM

import time


from ina219 import INA219

astraGpioSet = { 
                "AstraPwm1": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6, "chip":2, "pwm":1},
                "AstraPwm2": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6, "chip":2, "pwm":2}
}

class AstraPwm():
    def __init__(self, name):
        self.name = name
        self.ratio=0
        if name in astraGpioSet :
            self.inacaract=astraGpioSet[self.name]
        else:
            raise UnkownAstraGpio
        address = self.inacaract["address"]
        shunt_ohms = self.inacaract["shunt_ohms"]
        max_expected_amps = self.inacaract["max_expected_amps"]
        max_expected_amps = self.inacaract["max_expected_amps"]
         
        self.ina219=INA219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
        self.pwm =  SysPWM(self.inacaract["chip"],self.inacaract["pwm"])
        self.pwm.set_duty_ms(0)
        self.pwm.set_periode_ms(100)

    def current(self):
        return self.ina219.current()

    def shunt_voltage(self):
        return self.ina219.shunt_voltage()

    def voltage(self):
        return self.ina219.voltage()

    def power(self):
        return self.ina219.power()

    def print_status(self):
        print(self.name,":",self.gpioline.name(), ":", self.gpioline.get_value(), "=>", self.voltage(), "V", self.current(), "mA")

    def get_name(self):
        return self.gpioline.name()

    def get_name(self):
        return self.name

    def set_ratio(self, ratio):
        intratio = int(ratio)
        if intratio < 0:
            intratio=0
        elif intratio > 100:
            intratio = 100
        self.ratio=intratio
        self.pwm.set_periode_ms(self.ratio)

    def get_ratio(self):
        return self.ratio

if __name__ == '__main__':

    astrapwm1=AstraPwm("AstraPwm1")
    astrapwm2=AstraPwm("AstraPwm2")

    duty=0
    while True:
        astrapwm1.set_ratio(duty)
        astrapwm2.set_ratio(100-duty)
        time.sleep(1)
    


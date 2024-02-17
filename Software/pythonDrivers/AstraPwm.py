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

class AstraPwm(INA219):
    def __init__(self, name, MinTemp=-10, MaxTemp=20):
        self.name = name
        if name in astraGpioSet :
            self.inacaract=astraGpioSet[self.name]
        else:
            raise UnkownAstraGpio
        address = self.inacaract["address"]
        shunt_ohms = self.inacaract["shunt_ohms"]
        max_expected_amps = self.inacaract["max_expected_amps"]
        max_expected_amps = self.inacaract["max_expected_amps"]
        super().__init__(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)

        
        self.ratio=0
        self.period_ms=1.0
         
        self.pwm =  SysPWM(self.inacaract["chip"],self.inacaract["pwm"])
        self.pwm.set_duty_ms(0)
        self.pwm.set_periode_ms(self.period_ms)
        self.configure()

    def print_status(self):
        print(self.name,":", self.ratio, "=>", self.voltage(), "V", self.current(), "mA")

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
        print("Ratio:",self.ratio) 
        self.pwm.set_duty_ms(self.period_ms*self.ratio/100.0)
        #self.pwm.set_duty_ms(self.ratio/10.0)

    def get_ratio(self):
        return self.ratio

    def set_cmdTemp(self, set_cmdTemp):
        self.cmdTemp = set_cmdTemp

    def get_Temp(self):
        return self.cmdTemp

if __name__ == '__main__':

    astrapwm1=AstraPwm("AstraPwm1")
    astrapwm2=AstraPwm("AstraPwm2")

    duty=0
    while True:
        astrapwm1.set_ratio(duty)
        astrapwm1.print_status()
        astrapwm2.set_ratio(100-duty)
        astrapwm2.print_status()
        #duty=(duty+1)%101
        time.sleep(1)
    


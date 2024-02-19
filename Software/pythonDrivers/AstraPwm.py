#!/bin/env python3
# GPIO used PA17

from ina219 import INA219
from syspwm import SysPWM
import glob
import os
import time


from ina219 import INA219

astraGpioSet = { 
                "AstraPwm1": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6, "chip":2, "pwm":1},
                "AstraPwm2": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6, "chip":2, "pwm":2}
}

class AstraPwm():
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

        self.ina219=INA219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
         
        self.ratio=0
        self.period_ms=1.0
         
        self.pwm = SysPWM(self.inacaract["chip"],self.inacaract["pwm"])
        self.pwm.set_duty_ms(0)
        self.pwm.set_periode_ms(self.period_ms)
        self.ina219.configure()
        self.tempBaseDir = '/sys/bus/w1/devices/'        
        self.tempFile = ''

    def get_listTemp(self):
        listname=[]
        for path in glob.glob(self.tempBaseDir + '28*'):
            name=os.path.basename(path)
            listname.append(name)
        return listname

    def set_associateTemp(self, name):
        self.tempFile=self.tempBaseDir+name+"/w1_slave"
        if os.access(self.tempFile, os.R_OK):
            return True
        else:
            return False
        
    def _read_temp(self, path): 
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def get_temp(self):
        lines = self._read_temp(self.tempFile)
        retries = 5
        while (lines[0].strip()[-3:] != 'YES') and (retries > 0):
            time.sleep(0.1)
            lines = self._read_temp(self.tempFile)
            retries -= 1
        if retries == 0:
            return 998
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp = lines[1][equals_pos + 2:]
            return float(temp) / 1000
        else:
            return 999 # error

    def get_ina219(self):
        return self.ina219

    def print_status(self):
        print(self.name,":", self.ratio, "=>", self.ina219.voltage(), "V", self.ina219.current(), "mA")

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
        for name in astrapwm2.get_listTemp():
            astrapwm2.set_associateTemp(name)
            print(name,"=", astrapwm2.get_temp())
        #duty=(duty+1)%101
        time.sleep(1)
    


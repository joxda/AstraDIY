#!/bin/env python3
# GPIO used PA17

from powerIna219 import powerIna219
from syspwm import SysPWM
import threading
import glob
import os
import time
import atexit
import numpy as np




astraGpioSet = { 
                "AstraPwm1": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6, "chip":2, "pwm":1},
                "AstraPwm2": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6, "chip":2, "pwm":2}
}


class AstraTempFetcher(threading.Thread):
    _AstraTempFetcher=None
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.tableTemp = {}
        self.lock = threading.Lock()
        self.lock.acquire(True)

    @classmethod
    def get_instance(cls):
        if cls._AstraTempFetcher is None:
            cls._AstraTempFetcher = AstraTempFetcher()
            cls._AstraTempFetcher.start()
        return cls._AstraTempFetcher

    def run(self):
        def _read_temp(path):
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            return lines
        # Search devices
        for path in glob.glob('/sys/bus/w1/devices/28*'):
            name = os.path.basename(path)
            filename = path + "/w1_slave"
            if os.access(filename, os.R_OK):
                self.tableTemp[name] = {}
                self.tableTemp[name]["val"] = 0
                self.tableTemp[name]["file"] = path + "/w1_slave"
        self.running = True
        self.lock.release()
        # Run acquisition loop
        while self.running:
            for name in self.tableTemp.keys():
                tempFile = self.tableTemp[name]["file"]
                retries = 5
                returnval = 998
                while (returnval == 998) and (retries > 0):
                    lines = _read_temp(tempFile)
                    if (len(lines) == 2):
                        if (lines[0].strip()[-3:] == 'YES'):
                            equals_pos = lines[1].find('t=')
                            if equals_pos != -1:
                                temp = lines[1][equals_pos + 2:]
                                returnval = float(temp) / 1000
                    if (returnval == 998):
                        retries -= 1
                        time.sleep(0.1)
                if returnval != 998:
                    self.tableTemp[name]["val"] = returnval
            time.sleep(0.5)
            
    def stop(self):
        self.running = False
        self.join()

    def get_listTemp(self):
        with self.lock:
            return list(self.tableTemp.keys())

    def get_temp(self, tempname):
        return self.tableTemp[tempname]["val"]

    def get_default_temp(self):
        with self.lock:
            tempNames = list(self.tableTemp.keys())
            return self.tableTemp[tempNames[0]]["val"]


class AstraPwm():
    def __init__(self, name, MinTemp=-10, MaxTemp=20):
        self.name = name

        # Ina219 start
        if name in astraGpioSet :
            self.inacaract=astraGpioSet[self.name]
        else:
            raise Exception("Unkown AstraGpio")
        address = self.inacaract["address"]
        shunt_ohms = self.inacaract["shunt_ohms"]
        max_expected_amps = self.inacaract["max_expected_amps"]
        max_expected_amps = self.inacaract["max_expected_amps"]
        self.ina219=powerIna219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
        self.ina219.configure(bus_adc=powerIna219.ADC_64SAMP, shunt_adc=powerIna219.ADC_64SAMP)
        # End Ina219 start


        self.ratio=0
        self.period_ms=1
        #print("Init pwm:",self.inacaract["chip"],self.inacaract["pwm"])
        self.pwm = SysPWM(self.inacaract["chip"],self.inacaract["pwm"])
        self.pwm.set_duty_ms(0)
        self.pwm.set_periode_ms(self.period_ms)
        self.pwm.enable()
        atexit.register(self.pwm.disable)

        # Temp fetcher
        self.AstraTempFetcher = AstraTempFetcher.get_instance()
        self.tempname= self.AstraTempFetcher.get_default_temp()


        # Aserv
        self.cmdTemp=0
        self.poids_objet = 1
        self.puissance_max = 12*3
        self._running = False

    def get_listTemp(self):
       return self.AstraTempFetcher.get_listTemp()

    def get_temp(self):
        return self.AstraTempFetcher.get_temp(self.tempname)

    def set_associateTemp(self, name):
        if name in self.AstraTempFetcher.get_listTemp():
            self.tempname = name
            return True
        else:
            return False

    def get_ina219(self):
        return self.ina219

    def print_status(self):
        try:
            shunt_voltage = self.ina219.shunt_voltage()
            bus_voltage = self.ina219.voltage()
            current = self.ina219.current()
            power = self.ina219.power()
            TargetVoltage=self.ratio*12/100
            energie=self.ina219.energie()/3600
            print(f"{self.name}:{self.ratio} TargetVoltage={TargetVoltage}, =>Bus{bus_voltage:+.3f}V , Current: {current:+.3f}mA, Power: {power:.3f}mW, Power: {power:.3f}mWh")
        except:
            print("!!!!!!!!!!!!!!!")

    # set output
    def get_name(self):
        return self.gpioline.name()

    def get_name(self):
        return self.name

    def set_ratio(self, ratio):
        self.ratio=max(0, min(100,int(ratio)))
        duty=self.period_ms*self.ratio/100.0
        self.pwm.set_duty_ms(duty)

    def get_ratio(self):
        return self.ratio


    # Control temperature
    def set_cmdTemp(self, set_cmdTemp):
        try:
            self.cmdTemp = int(set_cmdTemp)
        except:
            pass

    def get_cmdTemp(self):
        return self.cmdTemp

    def _auto_tune_pid_lms(self):
        # Initialisation des coefficients PID
        Kp = 1.0
        Ki = 0.0
        Kd = 0.0
        step_time = 1.0
        learning_rate = 1 / (self.poids_objet * self.puissance_max)
        lastpid_output=0

        integral = 0.0  # Valeur initiale de l'intégrale glissante
        prev_error = 0.0

        while self._running:
            error = self.get_cmdTemp() - self.get_temp()

            # Calcul de l'intégrale glissante
            integral = 0.9 * integral + error

            # Calcul de la sortie du PID avec les coefficients PID actuels
            pid_output = Kp * error + Ki * integral + Kd * (error - prev_error)

            # Gestion de la saturation de pid_output entre 0 et 100
            pid_output = max(0, min(pid_output, 100))

            # Mise à jour des coefficients PID si la sortie n'est pas saturée
            if pid_output < 100 and pid_output > 0:
                Kp -= learning_rate * error
                Ki += learning_rate * integral
                Kd -= learning_rate * (error - prev_error)
                # Gestion de la saturation des coefficients PID entre 0 et 100
                Kp = max(0, min(Kp, 100))
                Ki = max(0, min(Ki, 100))
                Kd = max(0, min(Kd, 100))

            pid_output = max(0, min(pid_output, 100))
            print("cmd=", self.get_cmdTemp(), "Temp=", self.get_temp(), "pid=",pid_output)
            self.set_ratio(pid_output)
            time.sleep(step_time)



    def startAserv(self):
        if not self._running:
            self._running = True
            threading.Thread(target=self._auto_tune_pid_lms).start()

    def stopAserv(self):
        self._running = False


if __name__ == '__main__':

    astrapwm1=AstraPwm("AstraPwm1")
    astrapwm2=AstraPwm("AstraPwm2")
    modulo=50
    duty=0
    while True:
        astrapwm1.set_ratio(duty%modulo)
        astrapwm1.print_status()
        astrapwm2.set_ratio((100-duty)%modulo)
        astrapwm2.print_status()
        for name in astrapwm2.get_listTemp():
            astrapwm2.set_associateTemp(name)
            print(name,"=", astrapwm2.get_temp())
        duty=(duty+1)%101
        time.sleep(1)
    


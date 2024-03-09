#!/bin/env python3
# GPIO used PA17

from powerIna219 import powerIna219
from syspwm import SysPWM
import threading
import glob
import os
from pathlib import Path
import time
import atexit
import numpy as np
import json




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
    def __init__(self, name, MinTemp=0, MaxTemp=20):
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
        self.Kp = 2
        self.Ki = 0.0
        self.Kd = 0.0
        self.cmdTemp=0
        self.poids_objet = 1
        self.puissance_max = 12*3
        self.minTemp = MinTemp
        self.maxTemp = MaxTemp
        self._running = False
        self.load()

    def end(self):
        self.stopAserv()
        self.AstraTempFetcher.stop()

    def get_listTemp(self):
       return self.AstraTempFetcher.get_listTemp()

    def get_temp(self):
        return self.AstraTempFetcher.get_temp(self.tempname)

    def get_associateTemp(self):
        return self.tempname

    def _set_associateTemp(self, name):
        if name in self.AstraTempFetcher.get_listTemp():
            self.tempname = name
            return True
        else:
            return False

    def set_associateTemp(self, name):
        if self._set_associateTemp(name):
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
        self.ratio=max(0, min(100,int(ratio*10)/10))
        duty=self.period_ms*self.ratio/100.0
        self.pwm.set_duty_ms(duty)
        #print("AstraPwm.set_ratio(",self.ratio,")","=>",duty)
        

    def get_ratio(self):
        #print("AstraPwm.get_ratio(",self.ratio,")")
        return int(self.ratio)


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
        step_time = 3.0
        learning_rate = 0.00001
        lastpid_output=0

        error = self.get_cmdTemp() - self.get_temp()
        integralNbVal = 10
        integral = error * integralNbVal  # Valeur initiale de l'intégrale glissante
        integralList = [error] * integralNbVal
        prev_error = 0.0

        while self._running:
            error = self.get_cmdTemp() - self.get_temp()
            integralList.append(error)
            # Calcul de l'intégrale glissante
            integral = integral - integralList.pop(0) + error

            # Calcul de la sortie du PID avec les coefficients PID actuels
            pid_output = self.Kp * error + self.Ki * integral + self.Kd * (error - prev_error)

            # Gestion de la saturation de pid_output entre 0 et 100
            pid_output = max(0, min(pid_output, 100))

            # Mise à jour des coefficients PID si la sortie n'est pas saturée
            if pid_output < 100 and pid_output > -100:
                self.Kp -= learning_rate * error
                self.Ki += learning_rate * integral
                self.Kd -= learning_rate * (error - prev_error)
                # Gestion de la saturation des coefficients PID entre 0 et 100
                self.Kp = max(0, min(self.Kp, 100))
                self.Ki = max(0, min(self.Ki, 100))
                self.Kd = max(0, min(self.Kd, 100))

            pid_output = max(0, min(pid_output, 100))
            print("cmd=", self.get_cmdTemp(), "Temp=", self.get_temp(), f"pid={pid_output:.2f}   Kp={self.Kp:.3f} Ki={self.Ki:.3f} Kd={self.Kd:.3f} int:{integral:.1f}")
            self.set_ratio(pid_output)
            time.sleep(step_time)
        self.set_ratio(0)

    def startAserv(self):
        if not self._running:
            self._running = True
            self.thread = threading.Thread(target=self._auto_tune_pid_lms)
            self.thread.start()

    def stopAserv(self):
        self._running = False
        #if hasattr(self, 'thread') and self.thread.is_alive():
        #    self.thread.join()

    def isAserv(self):
        return self._running


    def load(self):
        variables_dict = {}
        filename = "sauve"+self.name+".json"
        chemin_complet=Path.home() / ".AstrAlim"  / filename
        if chemin_complet.exists():
            with open(chemin_complet, "r") as f:
                variables_dict = json.load(f)
            if "Kp" in variables_dict and "Ki"  in variables_dict  and "Kd"  in variables_dict:
                self.Kp = variables_dict["Kp"]
                self.Ki = variables_dict["Ki"]
                self.Kd = variables_dict["Kd"]
            if "tempname" in variables_dict:
                return self._set_associateTemp(variables_dict["tempname"])
            else:
                return False
        else:
            return False



    def save(self):
        variables_dict = {}
        variables_dict = {
                "name":self.name, 
                "tempname":self.tempname,
                "Kp":self.Kp,
                "Ki":self.Ki,
                "Kd":self.Kd,
                }
        chemin_complet=Path.home() / ".AstrAlim"
        chemin_complet.mkdir(parents=True, exist_ok=True)
        filename = "sauve"+self.name+".json"
        chemin_complet = chemin_complet / filename
        with open(chemin_complet, "w") as f:
            json.dump(variables_dict, f, indent=4)


        

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
    


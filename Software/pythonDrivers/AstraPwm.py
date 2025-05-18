#!/bin/env python3
# GPIO used PA17
from syspwm import SysPWM
import threading
import glob
import os
from pathlib import Path
import time
import atexit
import numpy as np
import json


from bme280_lib import readBME280All
import math


class AstraTempFetcher(threading.Thread):
    ROSEEUNAVAIL=-100
    TEMPUNAVAIL=100
    _AstraTempFetcher=None
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.tableTemp = {}
        self.lock = threading.Lock()
        #self.lock.acquire(True)
        self.bme_present=False
        self.bme_temperature=0
        self.bme_pressure=0
        self.bme_humidity=0
        self.bme_tempRosee=self.TEMPUNAVAIL


    @classmethod
    def get_instance(cls):
        if cls._AstraTempFetcher is None:
            cls._AstraTempFetcher = AstraTempFetcher()
            cls._AstraTempFetcher.start()
        return cls._AstraTempFetcher

    @classmethod
    def exitAll(cls):
        if not(cls._AstraTempFetcher is None):
            cls._AstraTempFetcher.stop()

    def _update_templist(self):
        # Search devices
        for path in glob.glob('/sys/bus/w1/devices/28*'):
            name = os.path.basename(path)
            filename = path + "/w1_slave"
            if os.access(filename, os.R_OK):
                with self.lock:
                    if os.access(filename, os.R_OK) and not name in self.tableTemp:
                        self.tableTemp[name] = {}
                        self.tableTemp[name]["val"] = 0
                        self.tableTemp[name]["file"] = path + "/w1_slave"

    def get_listTemp(self):
        with self.lock:
            return list(self.tableTemp.keys())

    def get_temp(self, tempname):
        with self.lock:
            val = self.TEMPUNAVAIL
            if tempname in  self.tableTemp:
                val = self.tableTemp[tempname]["val"]
        return val

    def run(self):
        def _read_temp(path):
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            return lines
        self._update_templist()
        self.running = True
        # Run acquisition loop
        while self.running:
            for name in self.tableTemp.keys():
                tempFile = self.tableTemp[name]["file"]
                retries = 10
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
                else:
                    self.tableTemp[name]["val"] = self.TEMPUNAVAIL
            try:
                self.bme_temperature,self.bme_pressure,self.bme_humidity = readBME280All()
                # ref : https://fr.planetcalc.com/248/
                # ref : https://fr.wikipedia.org/wiki/Point_de_ros%C3%A9e
                a=17.27
                b=237.7
                facteur=((a*self.bme_temperature) / (b+self.bme_temperature)) + math.log(self.bme_humidity/100)
                self.bme_tempRosee = b*(facteur)/(a-(facteur))
                self.bme_present = True
            except Exception as e:
                # print(e)
                self.bme_present=False
                self.bme_tempRosee=self.ROSEEUNAVAIL
                self.bme_temperature=self.TEMPUNAVAIL
                pass
            self._update_templist()
            time.sleep(1)

            
    def stop(self):
        self.running = False
        self.join()
        AstraTempFetcher._AstraTempFetcher = None


    def get_default_temp(self):
        with self.lock:
            tempNames = list(self.tableTemp.keys())
            if len(tempNames) > 0:
                return self.tableTemp[tempNames[0]]["val"]
            else:
                return None

    def get_bmeTemp(self):
        return self.bme_temperature

    def get_bmePressure(self):
        return self.bme_pressure

    def get_bmeHumidity(self):
        return self.bme_humidity

    def get_bmeTempRosee(self):
        return self.bme_tempRosee

    def isPresent_bme(self):
        return self.bme_present

class RaspberryPiModel:
    def __init__(self):
        self.compatible_strings = self._read_compatible_strings()

    def _read_compatible_strings(self):
        try:
            with open('/proc/device-tree/compatible', 'r') as file:
                return file.read().split('\x00')
        except FileNotFoundError:
            return []

    def getModelNumber(self):
        for string in self.compatible_strings:
            if string.startswith('raspberrypi,'):
                # Extract the model number from the string
                model_number = string.split(',')[1].split('-')[0]
                return model_number
        return "Unknown Model"
    
    def getPi(self):
        """
        Return the string pi followd by the number of the pi. (E.g.: pi4)
        """

        return f"pi{self.getModelNumber()}"
    
class AstraPwm():
    ROSEEUNAVAIL=AstraTempFetcher.ROSEEUNAVAIL
    TEMPUNAVAIL=AstraTempFetcher.TEMPUNAVAIL
    astraGpioSet = { 
                "AstraPwm1": {
                    "pi5": { "chip":2, "pwm":1 },
                    "pi4": { "chip":0, "pwm":0 },
                              },
                "AstraPwm2": {
                    "pi5": { "chip":2, "pwm":2 },
                    "pi4": { "chip":0, "pwm":1 },
                }
    }

    def __init__(self, name, MinTemp=0, MaxTemp=20):
        self.name = name
        self.piModel=RaspberryPiModel().getPi()
        if name in self.astraGpioSet :
            if self.piModel in self.astraGpioSet[self.name]:
                self.inacaract=self.astraGpioSet[self.name][self.piModel]
            else:
                raise Exception(f"Not compatible pi model : {self.piModel}")
        else:
            raise Exception("Unkown AstraGpio")


        self.ratio=0
        self.period_ms=1
        self.pwm = SysPWM(self.inacaract["chip"],self.inacaract["pwm"])
        if self.pwm.get_periode_ms() > 0:
            self.pwm.set_duty_ms(0)
        self.pwm.set_periode_ms(self.period_ms)
        self.pwm.enable()
        atexit.register(self.pwm.disable)

        # Temp fetcher
        self.AstraTempFetcher = AstraTempFetcher.get_instance()
        self.tempname= self.AstraTempFetcher.get_default_temp()

        # Temp Rosee setup
        self.deltaTempRosee=+2
        self.asservTempRosee = True

        # Aserv
        self.thread=None
        self.autoUpdateKpKiKd=True
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
        self.set_ratio(0)
        self.AstraTempFetcher.stop()

    ######## Accessors 
    def get_name(self):
        return self.name

    # Control temperature command
    def set_cmdTemp(self, set_cmdTemp):
        try:
            self.cmdTemp = int(set_cmdTemp)
        except:
            pass

    def get_cmdTemp(self):
        return self.cmdTemp

    def get_deltaTempRosee(self):
        return self.deltaTempRosee

    def set_asservTempRosee(self):
        self.asservTempRosee = True

    def unset_asservTempRosee(self):
        self.asservTempRosee = False

    def set_deltaTempRosee(self, deltaTempRosee):
        self.deltaTempRosee=deltaTempRosee

    def updateCmdTempfromTempRosee(self):
        if self.asservTempRosee: 
            self.cmdTemp = self.get_bmeTempRosee() + self.deltaTempRosee

    # Asserv Parameters
    def get_autoUpdateKpKiKd(self):
        return self.autoUpdateKpKiKd

    def set_autoUpdateKpKiKd(self):
        self.autoUpdateKpKiKd=True

    def unset_autoUpdateKpKiKd(self):
        self.autoUpdateKpKiKd=False

    def get_Kp(self):
        return self.Kp

    def set_kp(self, Kp):
        self.Kp=max(0, min(self.Kp, 100))

    def get_Ki(self):
        return self.Ki

    def set_Ki(self, Ki):
        self.Ki=max(0, min(self.Ki, 100))

    def get_Kd(self):
        return self.Kd

    def set_Kd(self, Kd):
        self.Kd=max(0, min(self.Kd, 100))

    # Associated sensor
    def get_listTemp(self):
       return self.AstraTempFetcher.get_listTemp()

    def get_temp(self):
        return self.AstraTempFetcher.get_temp(self.tempname)

    def get_associateTemp(self):
        return self.tempname

    def _set_associateTemp(self, name):
        retval = False
        iteration=4
        #while ((iteration > 0) and (not(retval))):
        #    if name in self.AstraTempFetcher.get_listTemp():
        #        self.tempname = name
        #        retval= True
        #    else:
        #        time.sleep(0.1)
        self.tempname = name
        retval=True
        return retval

    def set_associateTemp(self, name):
        if self._set_associateTemp(name):
            return True
        else:
            return False

    # Environmental sensor
    def get_bmeTemp(self):
        return self.AstraTempFetcher.get_bmeTemp()

    def get_bmePressure(self):
        return self.AstraTempFetcher.get_bmePressure()

    def get_bmeHumidity(self):
        return self.AstraTempFetcher.get_bmeHumidity()

    def get_bmeTempRosee(self):
        return self.AstraTempFetcher.get_bmeTempRosee()

    def print_status(self):
        try:
            TargetVoltage=self.ratio*12/100
            print(f"{self.name}:{self.ratio} TargetVoltage={TargetVoltage}")
        except:
            print("!!!!!!!!!!!!!!!")

    # set output
    def set_ratio(self, ratio):
        self.ratio=max(0, min(100,int(ratio*10)/10))
        duty=self.period_ms*self.ratio/100.0
        self.pwm.set_duty_ms(duty)
        #print("AstraPwm.set_ratio(",self.ratio,")","=>",duty)

    def get_ratio(self):
        #print("AstraPwm.get_ratio(",self.ratio,")")
        return int(self.ratio)

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
            self.updateCmdTempfromTempRosee()
            error = self.get_cmdTemp() - self.get_temp()
            integralList.append(error)
            # Calcul de l'intégrale glissante
            integral = integral - integralList.pop(0) + error

            # Calcul de la sortie du PID avec les coefficients PID actuels
            pid_output = self.Kp * error + self.Ki * integral + self.Kd * (error - prev_error)

            # Gestion de la saturation de pid_output entre 0 et 100
            pid_output = max(0, min(pid_output, 100))

            # Mise à jour des coefficients PID si la sortie n'est pas saturée
            if self.autoUpdateKpKiKd and pid_output < 100 and pid_output > -100:
                self.Kp -= learning_rate * error
                self.Ki += learning_rate * integral
                self.Kd -= learning_rate * (error - prev_error)
                # Gestion de la saturation des coefficients PID entre 0 et 100
                self.Kp = max(0, min(self.Kp, 100))
                self.Ki = max(0, min(self.Ki, 100))
                self.Kd = max(0, min(self.Kd, 100))

            pid_output = max(0, min(pid_output, 100))
            #print("cmd=", self.get_cmdTemp(), "Temp=", self.get_temp(), f"pid={pid_output:.2f}   Kp={self.Kp:.3f} Ki={self.Ki:.3f} Kd={self.Kd:.3f} int:{integral:.1f}")
            self.set_ratio(pid_output)
            time.sleep(step_time)
        self.set_ratio(0)

    def startAserv(self):
        if not self._running:
            # test If I did launch a thread previously and wait for it to end
            if self.thread != None:
                self.thread.join()    
            self._running = True
            self.thread = threading.Thread(target=self._auto_tune_pid_lms)
            self.thread.start()

    def stopAserv(self):
        if self._running:
            self._running = False
            

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
    import signal
    import sys

    
    print(f"Running on : {RaspberryPiModel().getPi()}")
  
    astrapwm1=AstraPwm("AstraPwm1")
    astrapwm2=AstraPwm("AstraPwm2")
    
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        astrapwm1.end()
        astrapwm2.end()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

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
        print("bmeTemp=", astrapwm1.get_bmeTemp(), "bmeHum=", astrapwm1.get_bmeHumidity(), "Rosee=", astrapwm1.get_bmeTempRosee())
        duty=(duty+1)%101
        time.sleep(1)
    


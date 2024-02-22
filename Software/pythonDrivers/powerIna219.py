#!/bin/env python3
# GPIO used PA17
import logging
from ina219 import INA219
import threading
import time


global listIna219
global powerthreadContinue
powerthreadContinue=True
listIna219 = []
listIna219lock = threading.Lock()

def powerthread():
    locallist=[]
    lasttime=time.perf_counter()
    time.sleep(0.5)
    while powerthreadContinue:
        with listIna219lock:
            locallist=listIna219
        for ina in locallist:
            if ina["lasttime"] == 0:
                ina["lasttime"] = time.perf_counter()
            else:
                curtime=time.perf_counter()
                deltatime=curtime-ina["lasttime"]
                ina["voltage"] = ina["ina219"].voltage()
                ina["shunt_voltage"] = ina["ina219"].shunt_voltage()
                ina["current"] = ina["ina219"].current()
                ina["power"] = ina["ina219"].power()
                ina["energie"] += ina["power"] * deltatime 
                ina["lasttime"]=curtime
                #print(ina["address"]," voltage", ina["voltage"])

def stoppowerthread():
    powerthreadContinue=False

    
powerIna219Thread = threading.Thread(target=powerthread, daemon=True)
powerIna219Thread.start()



class powerIna219:
    RANGE_16V = INA219.RANGE_16V  # Range 0-16 volts
    RANGE_32V = INA219.RANGE_32V  # Range 0-32 volts

    GAIN_1_40MV = INA219.GAIN_1_40MV  # Maximum shunt voltage 40mV
    GAIN_2_80MV = INA219.GAIN_2_80MV  # Maximum shunt voltage 80mV
    GAIN_4_160MV = INA219.GAIN_4_160MV  # Maximum shunt voltage 160mV
    GAIN_8_320MV = INA219.GAIN_8_320MV  # Maximum shunt voltage 320mV
    GAIN_AUTO = INA219.GAIN_AUTO  # Determine gain automatically

    ADC_9BIT = INA219.ADC_9BIT  # 9-bit conversion time  84us.
    ADC_10BIT = INA219.ADC_10BIT  # 10-bit conversion time 148us.
    ADC_11BIT = INA219.ADC_11BIT  # 11-bit conversion time 2766us.
    ADC_12BIT = INA219.ADC_12BIT  # 12-bit conversion time 532us.
    ADC_2SAMP = INA219.ADC_2SAMP  # 2 samples at 12-bit, conversion time 1.06ms.
    ADC_4SAMP = INA219.ADC_4SAMP  # 4 samples at 12-bit, conversion time 2.13ms.
    ADC_8SAMP = INA219.ADC_8SAMP  # 8 samples at 12-bit, conversion time 4.26ms.
    ADC_16SAMP = INA219.ADC_16SAMP  # 16 samples at 12-bit,conversion time 8.51ms
    ADC_32SAMP = INA219.ADC_32SAMP  # 32 samples at 12-bit, conversion time 17.02ms.
    ADC_64SAMP = INA219.ADC_64SAMP  # 64 samples at 12-bit, conversion time 34.05ms.
    ADC_128SAMP = INA219.ADC_128SAMP  # 128 samples at 12-bit, conversion time 68.10ms.


    def __init__(self, shunt_ohms, max_expected_amps, busnum, address, log_level=logging.ERROR):
        self.ina219 = {"lasttime":0, "address":address, "voltage":0, "shunt_voltage":0, "current":0, "power":0, "energie":0}
        self.ina219["ina219"]= INA219(shunt_ohms, max_expected_amps, busnum, address, log_level)
        self.configured=False

    def configure(self, voltage_range=INA219.RANGE_32V, gain=INA219.GAIN_AUTO, bus_adc=INA219.ADC_12BIT, shunt_adc=INA219.ADC_12BIT):
        if self.configured:
            raise Exception("powerIna219 already Configured")
        else:
            self.configured=True
            self.ina219["ina219"].configure(voltage_range, gain, bus_adc, shunt_adc)
            with listIna219lock:
                listIna219.append(self.ina219)

    def voltage(self):
        return self.ina219["voltage"]

    def shunt_voltage(self):
        return self.ina219["shunt_voltage"]

    def current(self):
        return self.ina219["current"]

    def power(self):
        return self.ina219["power"]

    def energie(self):
        return self.ina219["energie"]

if __name__ == "__main__":
    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    ina219_set = {
        "alim_1_i2c_41   ": {"address": 0x41, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_2_i2c_44   ": {"address": 0x44, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_3_i2c_45_5V": {"address": 0x46, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_4_i2c_47   ": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_5_i2c_47   ": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6}
    }


    # Créer une instance INA219Reader pour chaque capteur
    # Mettre à jour le dictionnaire ina219_addresses avec l'objet INA219Reader
    for name, info in ina219_set.items():
        address = info["address"]
        shunt_ohms = info["shunt_ohms"]
        max_expected_amps = info["max_expected_amps"]
        ina219_set[name]["ina219_object"] = powerIna219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
        ina219_set[name]["ina219_object"].configure(bus_adc=INA219.ADC_64SAMP, shunt_adc=INA219.ADC_64SAMP)

    while True:
        for name, info in ina219_set.items():
            ina219 = info["ina219_object"]
            shunt_voltage = ina219.shunt_voltage()
            bus_voltage = ina219.voltage()
            current = ina219.current()
            power = ina219.power()
            energie = ina219.energie() / 60 / 60

            print(f"{name}: Shunt {shunt_voltage:+.3f}V, Bus {bus_voltage:+.3f}V Current: {current:+.3f}A, Power: {power:.3f}mW Energie: {energie:.3f}mWh ")
            time.sleep(1)




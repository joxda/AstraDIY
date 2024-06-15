#!/bin/env python3
# GPIO used PA17
import logging
from ina219 import INA219
import threading
import time


class AstraInaFetcher(threading.Thread):
    _AstraInaFetcher=None

    def __init__(self):
        super().__init__()
        self.running = True
        self.listInalock = threading.Lock()
        self.listIna = []

    @classmethod
    def get_instance(cls):
        if cls._AstraInaFetcher is None:
            cls._AstraInaFetcher = AstraInaFetcher()
            cls._AstraInaFetcher.start()
        return cls._AstraInaFetcher

    @classmethod
    def exitAll(cls):
        if not(cls._AstraInaFetcher is None):
            cls._AstraInaFetcher.stop()


    def run(self):
        while self.running:
            time.sleep(0.4)
            with self.listInalock:
                for ina in self.listIna:
                    ina["configured"] = False
                    if ina["ina219"].ping():
                        ina["pinged"]=True
                        if ina["NotYetPing"]:
                            ina["lasttime"] = time.perf_counter()
                            ina["firstttime"] = time.perf_counter()
                            ina["NotYetPing"]=False

                    if  ina["pinged"]:
                        ina["ina219"].configure(voltage_range=ina["voltage_range"], gain=ina["gain"], bus_adc=ina["bus_adc"], shunt_adc=ina["shunt_adc"])
                        ina["configured"] = True

                time.sleep(0.1)
                for ina in self.listIna:
                    if ina["configured"]:
                        curtime=time.perf_counter()
                        deltatime=curtime-ina["lasttime"]
                        ina["shunt_voltage"] = ina["ina219"].shunt_voltage()
                        ina["voltage"] = ina["ina219"].voltage()
                        ina["current"] = ina["ina219"].current()
                        ina["power"] = ina["ina219"].power()
                        ina["energie"] += ina["power"] * deltatime
                        ina["lasttime"]=curtime
                        ina["intPeriod"]=curtime-ina["firstttime"]
                    #print(ina["address"]," voltage", ina["voltage"])

    def stop(self):
        self.running=False
        self.join()
        AstraIna._AstraInaFetcher=None

    def set_ina(self, ina):
        ina["pinged"]=False
        ina["NotYetPing"]=True
        with self.listInalock:
            self.listIna.append(ina)


class AstraIna:
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

    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    ina219_set = {
            "AstraDc1": {"ispwm":False, "busnum":1, "address": 0x41, "shunt_ohms": 0.01, "max_expected_amps": 6, "pin": 37, 
                         "bus_adc":INA219.ADC_128SAMP, "shunt_adc":INA219.ADC_128SAMP },
            "AstraDc2": {"ispwm":False, "busnum":1, "address": 0x44, "shunt_ohms": 0.01, "max_expected_amps": 6, "pin": 38, 
                         "bus_adc":INA219.ADC_128SAMP, "shunt_adc":INA219.ADC_128SAMP },
            "AstraDc3": {"ispwm":False, "busnum":1, "address": 0x46, "shunt_ohms": 0.01, "max_expected_amps": 6, "pin": 40, 
                         "bus_adc":INA219.ADC_128SAMP, "shunt_adc":INA219.ADC_128SAMP },
            "AstraPwm1": {"ispwm":True, "busnum":1, "address": 0x49, "shunt_ohms": 0.01, "max_expected_amps": 6, "chip":2, "pwm":1, 
                         "bus_adc":INA219.ADC_128SAMP, "shunt_adc":INA219.ADC_128SAMP },
            "AstraPwm2": {"ispwm":True, "busnum":1, "address": 0x4d, "shunt_ohms": 0.01, "max_expected_amps": 6, "chip":2, "pwm":2, 
                         "bus_adc":INA219.ADC_128SAMP, "shunt_adc":INA219.ADC_128SAMP },
            "AstOnStep": {"ispwm":True, "busnum":1, "address": 0x40, "shunt_ohms": 0.005, "max_expected_amps": 6, "chip":2, "pwm":2, 
                         "bus_adc":INA219.ADC_128SAMP, "shunt_adc":INA219.ADC_128SAMP }
    }

    @classmethod
    def getListNames(cls):
        return AstraIna.ina219_set.keys()

    @classmethod
    def exitAll(cls):
        AstraInaFetcher.exitAll()

    def __init__(self, shunt_ohms=-1, max_expected_amps=-1, busnum=-1, address=-1, name="", log_level=logging.ERROR):
        self.ina219 = {"configured":False, "lasttime":0, "firsttime":0, "address":address, "voltage":0, "shunt_voltage":0, "current":0, "power":0, "energie":0, "intPeriod":0}
        if name == "":
            if shunt_ohms==-1 or max_expected_amps==-1 or busnum==-1 or address==-1:
                raise Exception("If name notspecified call AstraIna(shunt_ohms, max_expected_amps, busnum, address")
            self.ina219["ina219"]= INA219(shunt_ohms, max_expected_amps, busnum, address, log_level)
            self.configured=False
            self.name="Unkown"
            # Temp fetcher
            self.AstraInaFetcher = AstraInaFetcher.get_instance()
        else:
            self.name=name
            if name in self.ina219_set:
                self.caract=self.ina219_set[name]
                self.ina219["ina219"]= INA219(self.caract["shunt_ohms"], self.caract["max_expected_amps"], self.caract["busnum"], self.caract["address"], log_level)
                self.configured=False
                # Temp fetcher
                self.AstraInaFetcher = AstraInaFetcher.get_instance()
                self.configure(bus_adc=self.caract["bus_adc"], shunt_adc=self.caract["shunt_adc"])
            else:
                raise Exception("Unkown AstraIna")


    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def configure(self, voltage_range=INA219.RANGE_16V, gain=INA219.GAIN_AUTO, bus_adc=INA219.ADC_12BIT, shunt_adc=INA219.ADC_12BIT):
        if self.configured:
            raise Exception("AstraIna already Configured")
        else:
            self.configured=True
            self.ina219["voltage_range"]=voltage_range
            self.ina219["gain"]=gain
            self.ina219["bus_adc"]=bus_adc
            self.ina219["shunt_adc"]=shunt_adc
            self.AstraInaFetcher.set_ina(self.ina219)

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

    def intPeriod(self):
        return self.ina219["intPeriod"]
    
if __name__ == "__main__":
    import signal
    import sys

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        AstraIna.exitAll()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    newSyntax=True
    if newSyntax:
        print(AstraIna.getListNames())
        listIna=[]
        for name in AstraIna.getListNames():
            listIna.append(AstraIna(name=name))
        while True:
            time.sleep(1)
            print("===============================================================")
            for ina219 in listIna:
                name=ina219.get_name()
                shunt_voltage = ina219.shunt_voltage()
                bus_voltage = ina219.voltage()
                current = ina219.current()
                power = ina219.power()
                energie = ina219.energie() / 60 / 60
                intPeriod=ina219.intPeriod()

                print(f"{name}: Shunt {shunt_voltage:+.3f}V, Bus {bus_voltage:+.3f}V Current: {current:+.3f}A, Power: {power:.3f}mW Energie: {energie:.3f}mWh  intPeriod: {intPeriod:.3f}s")
    else:
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
            ina219_set[name]["ina219_object"] = AstraIna(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
            ina219_set[name]["ina219_object"].configure(bus_adc=INA219.ADC_64SAMP, shunt_adc=INA219.ADC_64SAMP)

        while True:
            time.sleep(1)
            print("===============================================================")
            for name, info in ina219_set.items():
                ina219 = info["ina219_object"]
                shunt_voltage = ina219.shunt_voltage()
                bus_voltage = ina219.voltage()
                current = ina219.current()
                power = ina219.power()
                energie = ina219.energie() / 60 / 60
                intPeriod=ina219.intPeriod()

                print(f"{name}: Shunt {shunt_voltage:+.3f}V, Bus {bus_voltage:+.3f}V Current: {current:+.3f}A, Power: {power:.3f}mW Energie: {energie:.3f}mWh intPeriod: {intPeriod:.3f}s")




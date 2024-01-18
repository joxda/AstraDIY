#!/bin/env python3

import smbus
import time

class INA219Reader:
    def __init__(self, i2c_bus=1, address=0x41, calibration=4096, shunt_ohms=0.02, max_expected_amps=6):
        self.bus = smbus.SMBus(i2c_bus)
        self.address = address
        self.calibration = calibration
        self.shunt_ohms = shunt_ohms
        self.max_expected_amps = max_expected_amps

        self.VoltageLast=0
        self.VoltageLastRead=False
        self.VoltageLSBV=0.004
        self.Voltagebusrange32=True

        try:
           # Calculer la valeur de calibration en fonction de la résistance de shunt et du courant maximal attendu
           self.current_lsb = max_expected_amps / 32768
           self.calibration_value = int(0.04096 / (self.current_lsb * shunt_ohms))

           # Configurer l'INA219
           # Mode = Shunt and bus, continuous
           config = 0b111 
           # 68.10 ms avrage for the shunt 
           config = (0b1111 << 3) | config 
           # 68.10 ms avrage for voltage
           config = (0b1111 << 7) | config 
           # ±320 mV Range PGA (Shunt Voltage Only)
           config = (0b11 << 11) | config 
           if self.Voltagebusrange32:
               # Bus Voltage Range 32V 
               config = (0b1 << 13) | config 
               self.VoltageLSBV = 0.004
           else:
               # Bus Voltage Range 16V 
               config = (0b0 << 13) | config 
               self.VoltageLSBV = 0.008
           # Forced config
           #config = (0b111 << 9) | (0b111 << 6) | 0b111  # Réglages de configuration
           #print(f"Config = {bin(config)}") 
           self.bus.write_i2c_block_data(self.address, 0x00, [(config >> 8) & 0xFF, config & 0xFF])

           # Écrire la valeur de calibration dans le registre CALIBRATION
           self.bus.write_i2c_block_data(self.address, 0x05, [(self.calibration_value >> 8) & 0xFF, self.calibration_value & 0xFF])

        except Exception as e:
            print(f"Erreur lors de l'initialisation du composant INA219 à l'adresse {hex(address)}: {str(e)}")


    def read_shunt_voltage(self):
        shunt_voltage = self.bus.read_word_data(self.address, 0x01)
        return shunt_voltage * 0.00001  # Conversion en volts

    def read_bus_voltage(self):
        bus_voltage = self.bus.read_word_data(self.address, 0x02)
        if (bus_voltage & 0b11) != 0b11:
           self.VoltageLastRead = False
        else:
           self.VoltageLastRead = True
           self.VoltageLast= (bus_voltage >> 3) * self.VoltageLSBV  # Conversion en volts
        return self.VoltageLast

    def read_current(self):
        current = self.bus.read_word_data(self.address, 0x04)
        return current * self.current_lsb  # Conversion en Ampères

    def read_power(self):
        power = self.bus.read_word_data(self.address, 0x03)
        return power * self.calibration_value * 20  # Conversion en mW

if __name__ == "__main__":
    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    ina219_set = {
        "alim_1_i2c_41": {"address": 0x41, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_2_i2c_44": {"address": 0x44, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_3_i2c_45_5V": {"address": 0x45, "shunt_ohms": 0.02, "max_expected_amps": 6},
        #"alim_4_i2c_47": {"address": 0x47, "shunt_ohms": 0.02, "max_expected_amps": 6}
    }


    # Créer une instance INA219Reader pour chaque capteur
    # Mettre à jour le dictionnaire ina219_addresses avec l'objet INA219Reader
    for name, info in ina219_set.items():
        address = info["address"]
        shunt_ohms = info["shunt_ohms"]
        max_expected_amps = info["max_expected_amps"]
        ina219_set[name]["ina219_object"] = INA219Reader(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps)


    while True:
        for name, info in ina219_set.items():
            ina219 = info["ina219_object"]
            shunt_voltage = ina219.read_shunt_voltage()
            bus_voltage = ina219.read_bus_voltage()
            current = ina219.read_current()
            power = ina219.read_power()

            print(f"{name}:")
            print(f"  Shunt Voltage: {shunt_voltage:.3f} V")
            print(f"  Bus Voltage: {bus_voltage:.3f} V")
            print(f"  Current: {current:.3f} A")
            print(f"  Power: {power:.3f} mW")
            print("")
        time.sleep(1)


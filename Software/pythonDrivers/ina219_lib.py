#!/bin/env python3

from ina219 import INA219
import time
import smbus


if __name__ == "__main__":
    # Dictionnaire associant les noms aux informations sur les capteurs INA219
    ina219_set = {
        "alim_1_i2c_41": {"address": 0x41, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_2_i2c_44": {"address": 0x44, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_3_i2c_45_5V": {"address": 0x46, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_4_i2c_47": {"address": 0x49, "shunt_ohms": 0.02, "max_expected_amps": 6},
        "alim_5_i2c_47": {"address": 0x4d, "shunt_ohms": 0.02, "max_expected_amps": 6}
    }


    # Créer une instance INA219Reader pour chaque capteur
    # Mettre à jour le dictionnaire ina219_addresses avec l'objet INA219Reader
    for name, info in ina219_set.items():
        address = info["address"]
        shunt_ohms = info["shunt_ohms"]
        max_expected_amps = info["max_expected_amps"]
        ina219_set[name]["ina219_object"] = INA219(address=address, shunt_ohms=shunt_ohms, max_expected_amps=max_expected_amps, busnum=1)
        ina219_set[name]["ina219_object"].configure()

    for name, info in ina219_set.items():
            ina219 = info["ina219_object"]
            shunt_voltage = ina219.shunt_voltage()
            bus_voltage = ina219.voltage()
            current = ina219.current()
            power = ina219.power()

            print(f"{name}:")
            print(f"  Shunt Voltage: {shunt_voltage:.3f} V")
            print(f"  Bus Voltage: {bus_voltage:.3f} V")
            print(f"  Current: {current:.3f} A")
            print(f"  Power: {power:.3f} mW")
            print("")


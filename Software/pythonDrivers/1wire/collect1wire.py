#!/usr/bin/python
import datetime

from DS18B20classfile import DS18B20

degree_sign = u'\xb0' # degree sign
devices = DS18B20()
count = devices.device_count()
names = devices.device_names()

i = 0
retry=3
while i < count:
	while retry > 0:
		try:
			container = devices.tempC(i)
			retry=-1	
		except IndexError:
			print('Error:')
			print(retry)
			pass
		else:
			print('{}. Temp: {:.3f}C,  of the device {}' .format(i+1, container, names[i]))
			data = '{{"data":[{{"Capteur": "{}", "Value": "{:.3f}"}}]}}' .format(names[i], container)
			print(data)
		retry=retry-1
	i=i+1



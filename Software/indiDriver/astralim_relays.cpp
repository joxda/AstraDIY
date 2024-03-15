/*******************************************************************************
  Copyright(c) 2015-2021 Radek Kaczorek  <rkaczorek AT gmail DOT com>

 This library is free software; you can redistribute it and/or
 modify it under the terms of the GNU Library General Public
 License version 2 as published by the Free Software Foundation.
 .
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Library General Public License for more details.
 .
 You should have received a copy of the GNU Library General Public License
 along with this library; see the file COPYING.LIB.  If not, write to
 the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 Boston, MA 02110-1301, USA.
*******************************************************************************/

#include <stdio.h>
#include <memory>
#include <string.h>
#include "config.h"

#include "astralim_relays.h"

#include <gpiod.h>

// We declare an auto pointer to IndiAstrAlimRelays
std::unique_ptr<IndiAstrAlimRelays> indiAstrAlimRelays(new IndiAstrAlimRelays());

void ISPoll(void *p);

void ISInit()
{
	static int isInit = 0;

	if (isInit == 1)
		return;
	if(indiAstrAlimRelays.get() == 0)
	{
		isInit = 1;
		indiAstrAlimRelays.reset(new IndiAstrAlimRelays());
	}
}
void ISGetProperties(const char *dev)
{
        ISInit();
        indiAstrAlimRelays->ISGetProperties(dev);
}
void ISNewSwitch(const char *dev, const char *name, ISState *states, char *names[], int num)
{
        ISInit();
        indiAstrAlimRelays->ISNewSwitch(dev, name, states, names, num);
}
void ISNewText(	const char *dev, const char *name, char *texts[], char *names[], int num)
{
        ISInit();
        indiAstrAlimRelays->ISNewText(dev, name, texts, names, num);
}
void ISNewNumber(const char *dev, const char *name, double values[], char *names[], int num)
{
        ISInit();
        indiAstrAlimRelays->ISNewNumber(dev, name, values, names, num);
}
void ISNewBLOB (const char *dev, const char *name, int sizes[], int blobsizes[], char *blobs[], char *formats[], char *names[], int num)
{
	INDI_UNUSED(dev);
	INDI_UNUSED(name);
	INDI_UNUSED(sizes);
	INDI_UNUSED(blobsizes);
	INDI_UNUSED(blobs);
	INDI_UNUSED(formats);
	INDI_UNUSED(names);
	INDI_UNUSED(num);
}
void ISSnoopDevice (XMLEle *root)
{
	ISInit();
	indiAstrAlimRelays->ISSnoopDevice(root);
}
IndiAstrAlimRelays::IndiAstrAlimRelays()
{
	setVersion(VERSION_MAJOR,VERSION_MINOR);
}
IndiAstrAlimRelays::~IndiAstrAlimRelays()
{
	// Delete controls on options tab
	deleteProperty(BCMpinsNP.name);
	deleteProperty(ActiveStateSP.name);
	deleteProperty(RelayLabelsTP.name);
}
bool IndiAstrAlimRelays::Connect()
{
	// Init GPIO
	chip = gpiod_chip_open(gpio_chip_path);
	if (!chip)
	{
		DEBUG(INDI::Logger::DBG_SESSION, "Problem initiating AstrAlim Relays.");
		return false;
	}

	// verify BCM Pins are not used by other consumers
	for (unsigned int pin = 0; pin < 3; pin++)
	{
		if (gpiod_line_is_used(gpiod_chip_get_line(chip, BCMpinsN[pin].value)))
		{
			DEBUGF(INDI::Logger::DBG_ERROR, "%d BCM Pin %0.0f already used", pin, BCMpinsN[pin].value);
			gpiod_chip_close(chip);
			return false;
		}
	}

	// Select gpios
	gpio_relay1 = gpiod_chip_get_line(chip, BCMpinsN[0].value);
	gpio_relay2 = gpiod_chip_get_line(chip, BCMpinsN[1].value);
	gpio_relay3 = gpiod_chip_get_line(chip, BCMpinsN[2].value);

	// Set initial gpios direction and states
	gpiod_line_request_output(gpio_relay1, "1@astralim_relays", relayState[0]);
	gpiod_line_request_output(gpio_relay2, "2@astralim_relays", relayState[1]);
	gpiod_line_request_output(gpio_relay3, "3@astralim_relays", relayState[2]);

	// Lock BCM Pins setting
	BCMpinsNP.s = IPS_BUSY;
	IDSetNumber(&BCMpinsNP, nullptr);

	// Lock Active State setting
	ActiveStateSP.s = IPS_BUSY;
	IDSetSwitch(&ActiveStateSP, nullptr);

	// Lock Relay Labels setting
	RelayLabelsTP.s = IPS_BUSY;
	IDSetText(&RelayLabelsTP, nullptr);

	// Set polling timer
	SetTimer(pollingTime);

	DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays connected successfully.");

	return true;
}
bool IndiAstrAlimRelays::Disconnect()
{
	// Close GPIO
	gpiod_chip_close(chip);

	// Unlock BCM Pins setting
	BCMpinsNP.s=IPS_IDLE;
	IDSetNumber(&BCMpinsNP, nullptr);

	// Unlock Active State setting
	ActiveStateSP.s = IPS_IDLE;
	IDSetSwitch(&ActiveStateSP, nullptr);

	// Unlock Relay Labels setting
	RelayLabelsTP.s = IPS_IDLE;
	IDSetText(&RelayLabelsTP, nullptr);

	DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays disconnected successfully.");
	return true;
}
const char * IndiAstrAlimRelays::getDefaultName()
{
        return (char *)"AstrAlim Relays";
}
bool IndiAstrAlimRelays::initProperties()
{
	// We init parent properties first
	INDI::DefaultDevice::initProperties();

	IUFillNumber(&BCMpinsN[0], "BCMPIN08", "Relay 11", "%0.0f", 1, 27, 0, 26); // BCM26 = PIN37
	IUFillNumber(&BCMpinsN[1], "BCMPIN06", "Relay 12", "%0.0f", 1, 27, 0, 20); // BCM20 = PIN38
	IUFillNumber(&BCMpinsN[2], "BCMPIN07", "Relay 13", "%0.0f", 1, 27, 0, 21); // BCM21 = PIN40
	IUFillNumberVector(&BCMpinsNP, BCMpinsN, 3, getDeviceName(), "BCMPINS", "BCM Pins", OPTIONS_TAB, IP_RW, 0, IPS_IDLE);

	//IUFillText(&RelayLabelsT[0], "RELAYLABEL01", "Relay 21", "Relay 31");
	//IUFillText(&RelayLabelsT[1], "RELAYLABEL02", "Relay 22", "Relay 32");
	//IUFillText(&RelayLabelsT[2], "RELAYLABEL03", "Relay 23", "Relay 33");
	//IUFillTextVector(&RelayLabelsTP, RelayLabelsT, 3, getDeviceName(), "RELAYLABELS", "Relay Labels", OPTIONS_TAB, IP_RW, 60, IPS_IDLE);

	IUFillSwitch(&ActiveStateS[0], "ACTIVELO", "Low", ISS_ON);
	IUFillSwitch(&ActiveStateS[1], "ACTIVEHI", "High", ISS_OFF);
	IUFillSwitchVector(&ActiveStateSP, ActiveStateS, 2, getDeviceName(), "ACTIVESTATE", "Active State", OPTIONS_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);

	// Load options before connecting
	// load config before defining switches
	defineNumber(&BCMpinsNP);
	defineSwitch(&ActiveStateSP);
	// DGE defineText(&RelayLabelsTP);
	loadConfig();

	IUFillSwitch(&Switch1S[0], "SW1ON", "ON", ISS_OFF);
	IUFillSwitch(&Switch1S[1], "SW1OFF", "OFF", ISS_ON);
	//DGE IUFillSwitchVector(&Switch1SP, Switch1S, 2, getDeviceName(), "SWITCH_1", RelayLabelsT[0].text, MAIN_CONTROL_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);
	IUFillSwitchVector(&Switch1SP, Switch1S, 2, getDeviceName(), "SWITCH_1", "AstraDC1", MAIN_CONTROL_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);

	IUFillSwitch(&Switch2S[0], "SW2ON", "ON", ISS_OFF);
	IUFillSwitch(&Switch2S[1], "SW2OFF", "OFF", ISS_ON);
	// DGE IUFillSwitchVector(&Switch2SP, Switch2S, 2, getDeviceName(), "SWITCH_2", RelayLabelsT[1].text, MAIN_CONTROL_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);
	IUFillSwitchVector(&Switch2SP, Switch2S, 2, getDeviceName(), "SWITCH_2", "AstraDC2", MAIN_CONTROL_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);

	IUFillSwitch(&Switch3S[0], "SW3ON", "ON", ISS_OFF);
	IUFillSwitch(&Switch3S[1], "SW3OFF", "OFF", ISS_ON);
	// DGE IUFillSwitchVector(&Switch3SP, Switch3S, 2, getDeviceName(), "SWITCH_3", RelayLabelsT[2].text, MAIN_CONTROL_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);
	IUFillSwitchVector(&Switch3SP, Switch3S, 2, getDeviceName(), "SWITCH_3", "AstraDC3", MAIN_CONTROL_TAB, IP_RW, ISR_1OFMANY, 0, IPS_IDLE);


	// Set initial relays states to OFF
	for (int i=0; i < 3; i++) {
		relayState[i] = !activeState;
	}

	return true;
}
bool IndiAstrAlimRelays::updateProperties()
{
	// Call parent update properties first
	INDI::DefaultDevice::updateProperties();

	if (isConnected())
	{
		// We're connected
		defineSwitch(&Switch1SP);
		defineSwitch(&Switch2SP);
		defineSwitch(&Switch3SP);
	}
	else
	{
		// We're disconnected
		deleteProperty(Switch1SP.name);
		deleteProperty(Switch2SP.name);
		deleteProperty(Switch3SP.name);
	}
	return true;
}

void IndiAstrAlimRelays::ISGetProperties(const char *dev)
{
	INDI::DefaultDevice::ISGetProperties(dev);
}

bool IndiAstrAlimRelays::ISNewNumber (const char *dev, const char *name, double values[], char *names[], int n)
{
	// first we check if it's for our device
	if(strcmp(dev,getDeviceName())==0)
	{
	        // handle BCMpins
	        if (!strcmp(name, BCMpinsNP.name))
	        {
			unsigned int valcount = 3;

			if (isConnected())
			{
				DEBUG(INDI::Logger::DBG_WARNING, "Cannot set BCM Pins while device is connected.");
				return false;
			} else {
				for (unsigned int i = 0; i < valcount; i++)
				{
					// verify a number is a valid BCM Pin
					if ( values[i] < 1 || values[i] > 27 )
					{
						BCMpinsNP.s=IPS_ALERT;
						IDSetNumber(&BCMpinsNP, nullptr);
						DEBUGF(INDI::Logger::DBG_ERROR, "Value %0.0f is not a valid BCM Pin number!", values[i]);
						return false;
					}

					// Verify unique BCM Pin assignement
					for (unsigned j = i + 1; j < valcount; j++)
					{
						if ( values[i] == values[j] )
						{
							BCMpinsNP.s=IPS_ALERT;
							IDSetNumber(&BCMpinsNP, nullptr);
							DEBUG(INDI::Logger::DBG_ERROR, "You cannot assign the same BCM Pin twice!");
							return false;
						}
					}

					// verify BCM Pins are not used by other consumers
					chip = gpiod_chip_open("/dev/gpiochip0");
					if (chip)
					{
						struct gpiod_line *line = gpiod_chip_get_line(chip, values[i]);
						bool line_status = gpiod_line_is_used(line);
						gpiod_chip_close(chip);

						if (line_status)
						{
							BCMpinsNP.s=IPS_ALERT;
							IDSetNumber(&BCMpinsNP, nullptr);
							DEBUGF(INDI::Logger::DBG_ERROR, "%d BCM Pin %0.0f already used!", i, values[i]);
							return false;
						}
					} else {
						DEBUG(INDI::Logger::DBG_ERROR, "Problem initiating AstrAlim Relays.");
						return false;
					}
				}

				IUUpdateNumber(&BCMpinsNP,values,names,n);

				BCMpinsNP.s=IPS_OK;
				IDSetNumber(&BCMpinsNP, nullptr);
				DEBUGF(INDI::Logger::DBG_SESSION, "AstrAlim Relays BCM Pins set to Relay1: %0.0f, Relay2: %0.0f, Relay3: %0.0f", BCMpinsN[0].value, BCMpinsN[1].value, BCMpinsN[2].value);
				return true;
			}
        	}
	}

	return INDI::DefaultDevice::ISNewNumber(dev,name,values,names,n);
}
bool IndiAstrAlimRelays::ISNewSwitch (const char *dev, const char *name, ISState *states, char *names[], int n)
{
	// return value for relays setting
	int rv;

	// first we check if it's for our device
	if (!strcmp(dev, getDeviceName()))
	{
		// handle active state
		if (!strcmp(name, ActiveStateSP.name))
		{
			if (isConnected())
			{
				DEBUG(INDI::Logger::DBG_WARNING, "Cannot set Active State while device is connected.");
				return false;
			}

			IUUpdateSwitch(&ActiveStateSP, states, names, n);

			if ( ActiveStateS[0].s == ISS_ON )
			{
				activeState = 0;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays active state set to LOW");
				ActiveStateSP.s = IPS_OK;
				ActiveStateS[1].s = ISS_OFF;
				IDSetSwitch(&ActiveStateSP, NULL);
				return true;
			}
			if ( ActiveStateS[1].s == ISS_ON )
			{
				activeState = 1;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays active state set to HIGH");
				ActiveStateSP.s = IPS_IDLE;
				ActiveStateS[0].s = ISS_OFF;
				IDSetSwitch(&ActiveStateSP, NULL);
				return true;
			}
		}

		// handle relay 1
		if (!strcmp(name, Switch1SP.name))
		{
			IUUpdateSwitch(&Switch1SP, states, names, n);

			if ( Switch1S[0].s == ISS_ON )
			{
				rv = gpiod_line_set_value(gpio_relay1, activeState);
				if (rv != 0)
				{
					DEBUG(INDI::Logger::DBG_ERROR, "Error setting AstrAlim Relay #1");
					Switch1SP.s = IPS_ALERT;
					Switch1S[0].s = ISS_OFF;
					IDSetSwitch(&Switch1SP, NULL);
					return false;
				}
				relayState[0] =  activeState;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays #1 set to ON");
				Switch1SP.s = IPS_OK;
				Switch1S[1].s = ISS_OFF;
				IDSetSwitch(&Switch1SP, NULL);
				return true;
			}
			if ( Switch1S[1].s == ISS_ON )
			{
				rv = gpiod_line_set_value(gpio_relay1, !activeState);
				if (rv != 0)
				{
					DEBUG(INDI::Logger::DBG_ERROR, "Error setting AstrAlim Relay #1");
					Switch1SP.s = IPS_ALERT;
					Switch1S[1].s = ISS_OFF;
					IDSetSwitch(&Switch1SP, NULL);
					return false;
				}
				relayState[0] =  !activeState;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays #1 set to OFF");
				Switch1SP.s = IPS_IDLE;
				Switch1S[0].s = ISS_OFF;
				IDSetSwitch(&Switch1SP, NULL);
				return true;
			}
		}

		// handle relay 2
		if (!strcmp(name, Switch2SP.name))
		{
			IUUpdateSwitch(&Switch2SP, states, names, n);

			if ( Switch2S[0].s == ISS_ON )
			{
				rv = gpiod_line_set_value(gpio_relay2, activeState);
				if (rv != 0)
				{
					DEBUG(INDI::Logger::DBG_ERROR, "Error setting AstrAlim Relay #2");
					Switch2SP.s = IPS_ALERT;
					Switch2S[0].s = ISS_OFF;
					IDSetSwitch(&Switch2SP, NULL);
					return false;
				}
				relayState[1] =  activeState;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays #2 set to ON");
				Switch2SP.s = IPS_OK;
				Switch2S[1].s = ISS_OFF;
				IDSetSwitch(&Switch2SP, NULL);
				return true;
			}
			if ( Switch2S[1].s == ISS_ON )
			{
				rv = gpiod_line_set_value(gpio_relay2, !activeState);
				if (rv != 0)
				{
					DEBUG(INDI::Logger::DBG_ERROR, "Error setting AstrAlim Relay #2");
					Switch2SP.s = IPS_ALERT;
					Switch2S[1].s = ISS_OFF;
					IDSetSwitch(&Switch2SP, NULL);
					return false;
				}
				relayState[1] =  !activeState;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays #2 set to OFF");
				Switch2SP.s = IPS_IDLE;
				Switch2S[0].s = ISS_OFF;
				IDSetSwitch(&Switch2SP, NULL);
				return true;
			}
		}

		// handle relay 3
		if (!strcmp(name, Switch3SP.name))
		{
			IUUpdateSwitch(&Switch3SP, states, names, n);

			if ( Switch3S[0].s == ISS_ON )
			{
				rv = gpiod_line_set_value(gpio_relay3, activeState);
				if (rv != 0)
				{
					DEBUG(INDI::Logger::DBG_ERROR, "Error setting AstrAlim Relay #3");
					Switch3SP.s = IPS_ALERT;
					Switch3S[0].s = ISS_OFF;
					IDSetSwitch(&Switch3SP, NULL);
					return false;
				}
				relayState[2] =  activeState;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays #3 set to ON");
				Switch3SP.s = IPS_OK;
				Switch3S[1].s = ISS_OFF;
				IDSetSwitch(&Switch3SP, NULL);
				return true;
			}
			if ( Switch3S[1].s == ISS_ON )
			{
				rv = gpiod_line_set_value(gpio_relay3, !activeState);
				if (rv != 0)
				{
					DEBUG(INDI::Logger::DBG_ERROR, "Error setting AstrAlim Relay #3");
					Switch3SP.s = IPS_ALERT;
					Switch3S[1].s = ISS_OFF;
					IDSetSwitch(&Switch3SP, NULL);
					return false;
				}
				relayState[2] =  !activeState;
				DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays #3 set to OFF");
				Switch3SP.s = IPS_IDLE;
				Switch3S[0].s = ISS_OFF;
				IDSetSwitch(&Switch3SP, NULL);
				return true;
			}
		}

	}
	return INDI::DefaultDevice::ISNewSwitch (dev, name, states, names, n);
}
bool IndiAstrAlimRelays::ISNewText (const char *dev, const char *name, char *texts[], char *names[], int n)
{
	// first we check if it's for our device
	if (!strcmp(dev, getDeviceName()))
	{
		// handle relay labels
		if (!strcmp(name, RelayLabelsTP.name))
		{
			if (isConnected())
			{
				DEBUG(INDI::Logger::DBG_WARNING, "Cannot set labels while device is connected.");
				return false;
			}

			IUUpdateText(&RelayLabelsTP, texts, names, n);
			RelayLabelsTP.s=IPS_OK;
			IDSetText(&RelayLabelsTP, nullptr);
			DEBUG(INDI::Logger::DBG_SESSION, "AstrAlim Relays labels set . You need to save configuration and restart driver to activate the changes.");
			DEBUGF(INDI::Logger::DBG_DEBUG, "AstrAlim Relays labels set to Relay1: %s, Relay2: %s, Relay3: %s", RelayLabelsT[0].text, RelayLabelsT[1].text, RelayLabelsT[2].text, RelayLabelsT[3].text);

			return true;
		}
	}

	return INDI::DefaultDevice::ISNewText (dev, name, texts, names, n);
}
bool IndiAstrAlimRelays::ISNewBLOB (const char *dev, const char *name, int sizes[], int blobsizes[], char *blobs[], char *formats[], char *names[], int n)
{
	return INDI::DefaultDevice::ISNewBLOB (dev, name, sizes, blobsizes, blobs, formats, names, n);
}
bool IndiAstrAlimRelays::ISSnoopDevice(XMLEle *root)
{
	return INDI::DefaultDevice::ISSnoopDevice(root);
}
bool IndiAstrAlimRelays::saveConfigItems(FILE *fp)
{
	IUSaveConfigNumber(fp, &BCMpinsNP);
	IUSaveConfigText(fp, &RelayLabelsTP);
	IUSaveConfigSwitch(fp, &ActiveStateSP);
	IUSaveConfigSwitch(fp, &Switch1SP);
	IUSaveConfigSwitch(fp, &Switch2SP);
	IUSaveConfigSwitch(fp, &Switch3SP);

	return true;
}

void IndiAstrAlimRelays::TimerHit()
{
	if(isConnected())
	{
		udateSwitches();
		SetTimer(pollingTime);
	}
}

void IndiAstrAlimRelays::udateSwitches()
{
	int gpio_relay_status[3];
	
	gpio_relay_status[0] = gpiod_line_get_value(gpio_relay1);
	gpio_relay_status[1] = gpiod_line_get_value(gpio_relay2);
	gpio_relay_status[2] = gpiod_line_get_value(gpio_relay3);

	// handle active-low status
	for (int i=0; i < 3; i++) {
		if (activeState == 0)
			gpio_relay_status[i] = !gpio_relay_status[i];
	}

	// update relay switch #1
	if ( Switch1S[0].s != gpio_relay_status[0])
	{
		if (gpio_relay_status[0] == 1)
		{
			Switch1SP.s = IPS_OK;
			Switch1S[0].s = ISS_ON;
			Switch1S[1].s = ISS_OFF;
			IDSetSwitch(&Switch1SP, NULL);
		} else {
			Switch1SP.s = IPS_IDLE;
			Switch1S[0].s = ISS_OFF;
			Switch1S[1].s = ISS_ON;
			IDSetSwitch(&Switch1SP, NULL);
		}
	}

	// update relay switch #2
	if ( Switch2S[0].s != gpio_relay_status[1])
	{
		if (gpio_relay_status[1] == 1)
		{
			Switch2SP.s = IPS_OK;
			Switch2S[0].s = ISS_ON;
			Switch2S[1].s = ISS_OFF;
			IDSetSwitch(&Switch2SP, NULL);
		} else {
			Switch2SP.s = IPS_IDLE;
			Switch2S[0].s = ISS_OFF;
			Switch2S[1].s = ISS_ON;
			IDSetSwitch(&Switch2SP, NULL);
		}
	}

	// update relay switch #3
	if ( Switch3S[0].s != gpio_relay_status[2])
	{
		if (gpio_relay_status[2] == 1)
		{
			Switch3SP.s = IPS_OK;
			Switch3S[0].s = ISS_ON;
			Switch3S[1].s = ISS_OFF;
			IDSetSwitch(&Switch3SP, NULL);
		} else {
			Switch3SP.s = IPS_IDLE;
			Switch3S[0].s = ISS_OFF;
			Switch3S[1].s = ISS_ON;
			IDSetSwitch(&Switch3SP, NULL);
		}
	}

	DEBUGF(INDI::Logger::DBG_DEBUG, "Relay #1 status: %i - Switch #1 status: %i", gpio_relay_status[0], Switch1S[0].s);
	DEBUGF(INDI::Logger::DBG_DEBUG, "Relay #2 status: %i - Switch #1 status: %i", gpio_relay_status[1], Switch2S[0].s);
	DEBUGF(INDI::Logger::DBG_DEBUG, "Relay #3 status: %i - Switch #1 status: %i", gpio_relay_status[2], Switch3S[0].s);
}

#!/bin/env bash
FILESOURCE=$(dirname $0)

sudo ${FILESOURCE}/install_gps.sh
sudo ${FILESOURCE}/install_scripts.sh
sudo ${FILESOURCE}/install_bootConfig.sh
${FILESOURCE}/install_autostart.sh

# i2c 
#i2cdetect  -y 1



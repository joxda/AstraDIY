#!/bin/bash
FILESOURCE=$(dirname $0)
TARGETDIR=~/.config/autostart/
echo "Begin Installing Auto-Start Astra Hmi"
mkdir -p $TARGETDIR
cp ${FILESOURCE}/autostart/*.desktop $TARGETDIR
echo "End Installing Auto-Start Astra Hmi"


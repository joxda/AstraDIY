#!/bin/env bash
# https://ozzmaker.com/faq/how-do-i-change-the-baud-rate-on-the-gps-module/
#  sudo awk '/GPS/{print $10}' /var/log/chrony/tracking.log | gnuplot -p -e "plot '<cat'"

systemctl stop chrony
systemctl stop gpsd
echo -e -n "\xB5\x62\x06\x00\x14\x00\x01\x00\x00\x00\xD0\x08\x00\x00\x00\xC2\x01\x00\x07\x00\x03\x00\x00\x00\x00\x00\xC0\x7E" > /dev/ttyAMA0
systemctl start gpsd
systemctl start chrony



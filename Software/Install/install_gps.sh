#!/bin/bash
FILESOURCE=$(dirname $0)
echo "Begin Installing gps"
apt install -y gpsd chrony
cp ${FILESOURCE}/gps/etc_default_gpsd /etc/default/gpsd
cp ${FILESOURCE}/gps/etc_chrony_conf.d_chronyastralim.conf /etc/chrony/conf.d/chronyastralim.conf
systemctl restart gpsd
systemctl restart chrony
BOOTFILE=/boot/firmware/config.txt
if ! grep -q "pps-gpio" ${BOOTFILE} ; then
    echo "L'option pps-gpio n'est pas sur le fichier /boot/config.txt. Ajout en cours..."
    cat >> ${BOOTFILE}  << "END1"

# Begin AstrAlim gps
# /dev/pps0
dtoverlay=pps-gpio,gpiopin=25
dtparam=uart0=on
# End AstrAlim GPS

END1
   echo "Need to reboot for a full operational gps"
else
    echo "L'option existe déjà."
    echo "Vérifier l'allocation à la pin gpio 25 du pps"
    cat << "END2"
dtoverlay=pps-gpio,gpiopin=25
dtparam=uart0=on
END2
fi

echo "End Installing gps"


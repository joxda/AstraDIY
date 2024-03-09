#!/bin/bash
#
HOMEDIR=$(dirname $0)/..
INSTALLDIR=/opt/AstrAlim

cat > /etc/profile.d/AstrAlim.sh << END
# Environnement Python AstrAlim 
export PYTHONPATH=\$PYTHONPATH:$INSTALLDIR
export PATH=\$PATH:$INSTALLDIR
END

#Install dependency
sudo apt -y install python3-smbus 

# Installer les fichiers 
mkdir -p /opt/AstrAlim
for FILE in Astra*.py ina219.py syspwm.py
do
	cp ${HOMEDIR}/pythonDrivers/${FILE} $INSTALLDIR
done
chmod +x $INSTALLDIR/Astra*.py


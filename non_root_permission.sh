#!/bin/bash

# Inspiration: https://forum.armbian.com/topic/8714-gpio-not-working-for-non-root/?do=findComment&comment=86295
# Run this script to enable all users in Linux user group gpio to access the gpio pins

if [ "$UID" != "0" ]
then
	echo "Script must be run as root! quitting..."
	exit 1
fi

cat /etc/group | grep "gpio" 2>&1 > /dev/null || groupadd gpio
chgrp gpio /dev/gpiochip0
chmod g+rw /dev/gpiochip0

echo "All users in group 'gpio' can access the gpio pins"
exit 0

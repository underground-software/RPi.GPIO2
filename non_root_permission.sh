#!/bin/bash

# Inspiration: https://forum.armbian.com/topic/8714-gpio-not-working-for-non-root/?do=findComment&comment=86295
# Run this script to enable all users in Linux user group gpio to access the gpio pins

# NOTE: the changes made by this script do _not_ persist after reboot.
# Until we provide an automated solution, we suggest that one
# place this snippet of code in a script that runs at system startup.

if [ "$UID" != "0" ]
then
	echo "Script must be run as root! quitting..."
	exit 1
fi

cat /etc/group | grep "gpio" 2>&1 > /dev/null || groupadd gpio
chgrp gpio /dev/gpiochip0
chmod g+rw /dev/gpiochip0

echo "All users in group 'gpio' can access the gpio pins"
echo "Would you like to make this change persistent? (Y/N)"
while read input; do
  case "$input" in
        [Yy]) if [ ! -f /etc/rc.d/rc.local ]; then
                        echo "#!/bin/sh" >> /etc/rc.d/rc.local
                        chmod +x /etc/rc.d/rc.local
              fi
              if [[ $(cat /etc/rc.d/rc.local \
                  | grep -E "chgrp gpio /dev/gpiochip0|chmod g+rw /dev/gpiochip0" \
                  | wc -l) != 2 ]]; then
                        echo "chgrp gpio /dev/gpiochip0" >> /etc/rc.d/rc.local
                        echo "chmod g+rw /dev/gpiochip0" >> /etc/rc.d/rc.local
              fi
              break ;;
        [Nn]) break ;;
           *) echo "Please enter Y or N: " ;;
  esac
done
exit 0

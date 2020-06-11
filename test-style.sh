#!/bin/bash

FLAKE8_FLAGS=""

while getopts "v" FLAG; do
        case $FLAG in
        v)
                FLAKE8_FLAGS="$FLAKE8_FLAGS "
                ;;
        esac
done

SOURCES=""
scan() {
	echo "[SCAN] $1"
        flake8 "$FLAKE8_FLAGS" $1
        RES=$?
        if test "$RES" -ne "0"
        then
                exit 1
        fi
}

scan RPi/_GPIO.py
scan tests/test_gpio.py
scan tests/test_pwm.py

scan RPi/GPIO/__init__.py
scan RPi/GPIO_DEVEL/__init__.py

for f in $(ls examples)
do
	if [ "$f" != "__pycache__" ] && [ "$f" != "morse.py" ]
	then
		scan examples/"$f" 
	fi
done

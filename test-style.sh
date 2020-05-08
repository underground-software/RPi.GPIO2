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
        flake8 "$FLAKE8_FLAGS" $1
        RES=$?
        if test "$RES" -ne "0"
        then
                exit 1
        fi
}

scan RPi/_GPIO.py
scan tests/test_whitebox.py

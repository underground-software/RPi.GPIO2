#!/bin/bash

PYTEST_FLAGS=""

while getopts "sm" FLAG; do
        case $FLAG in
        s)
                PYTEST_FLAGS="$PYTEST_FLAGS -s"
                ;;
        m)
                PYTEST_FLAGS="$PYTEST_FLAGS --cov-report term-missing"
                ;;
        esac
done

pytest $PYTEST_FLAGS --cov=. tests/

RES=$?

exit $RES

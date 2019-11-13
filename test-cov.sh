#!/bin/bash

PYTEST_FLAGS=""

while getopts "s" FLAG; do
	case $FLAG in
	s)
		PYTEST_FLAGS="$PYTEST_FLAGS -s"
		;;
	esac
done

pytest $PYTEST_FLAGS --cov=. tests/

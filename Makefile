# Makefile to automate common testing procedures for RPi.GPIO2
# By Joel Savitz
# This is free software, see LICENSE for details

all: test

test: test-cov style

test-cov:
	@bash test-cov.sh -m && echo "FUNCTIONAL PASS" || echo "FAILURE IN UNIT TEST"

style:
	@bash test-style.sh && echo "AESTHETIC PASS"  || echo "FAILURE IN STYLE TEST"

.PHONY: all test unit-cov style


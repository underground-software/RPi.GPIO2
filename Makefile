all: test

test: unit-cov style
#@echo "MAKE TEST PASS"

unit-cov:
	@bash test-cov.sh -m && echo "FUNTIONAL PASS" || echo "FAILURE IN UNIT TEST"

style:
	@bash test-style.sh && echo "AESTHETIC PASS"  || echo "FAILURE IN STYLE TEST"

.PHONY: all test unit-cov style


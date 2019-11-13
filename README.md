## libgpiod-python-rpi

#### Summary:

This project implements a compatibility layer between RPi.GPIO syntax and libgpiod semantics.

#### Problem:

RPi.GPIO requires non-standard kernel patches that expose the GPIO registers to userspace via
a character device `/dev/gpiomem`. As this is not supported by the mainline Linux kernel, any
disribution targeting Raspberry Pi devices running the mainline kernel will not be compatible
with the RPi.GPIO library. As a large number of tutorials, especially those targeted at
beginners, demonstrate use of the RPi's GPIO pins by including RPi.GPIO syntax, this
incompatibility limits users to distributions build on a special downsteam kernel maintained
by the Rapberry Pi foundation. We would like to enable beginners on any Linux distribution
by allowing them to follow easily available tutorials.

#### Solution:
Using the provided module, one will be able to write python code to use the Raspberry Pi's
GPIO pins as if they were using the API imlpemented by RPi.GPIO, but instead using
libgpiod's python bindings. libgpiod provides a straightforward interface for interacting
with GPIO pins on supported devices via the mainline Linux kernel interface.


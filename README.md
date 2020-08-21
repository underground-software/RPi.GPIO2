## RPi.GPIO2

[![PyPI version](https://badge.fury.io/py/RPi.GPIO2.svg)](https://badge.fury.io/py/RPi.GPIO2)

#### Summary:

This project implements a compatibility layer between RPi.GPIO syntax and libgpiod semantics.

#### Problem:

RPi.GPIO requires non-standard kernel patches that expose the GPIO registers to userspace via
a character device `/dev/gpiomem`. As this is not supported by the mainline Linux kernel, any
distribution targeting Raspberry Pi devices running the mainline kernel will not be compatible
with the RPi.GPIO library. As a large number of tutorials, especially those targeted at
beginners, demonstrate use of the RPi's GPIO pins by including RPi.GPIO syntax, this
incompatibility limits users to distributions build on a special downstream kernel maintained
by the Rapberry Pi foundation. We would like to enable beginners on any Linux distribution
by allowing them to follow easily available tutorials.

#### Solution:
Using the provided module, one will be able to write python code to use the Raspberry Pi's
GPIO pins as if they were using the API implemented by RPi.GPIO, but instead using
libgpiod's python bindings. libgpiod provides a straightforward interface for interacting
with GPIO pins on supported devices via the mainline Linux kernel interface.

For more detailed information on the design and implementation of this library, please
refer to the [functional and technical specification](https://github.com/underground-software/RPi.GPIO2/blob/master/spec/spec.pdf).

### Notes:

Do not install `RPI.GPIO` via `pip3` as that will attempt to install the raspbian-only library
that motivated this project in the first place. If that package is installed alonside this one,
attempts to `import RPi.GPIO` will cause an error as python will attempt to import the wrong
package.

To install the python development dependencies, run `pip install -r requirements.txt`.

Use of a virtual env is recomended for a development setup. This will allow local installation
of the library via `pip install -e .` in the repository root.

The libgpiod python bindings must be installed and accessible from the development environment.
This package is not available via `pip install` and must be installed using the system package
manager.

To enable access non-root access to the gpio pins, use the provided `non_root_permission.sh`
script. Upon successful execution, any user in Linux user group 'gpio' will be able to access
the gpio pins via this library.

To view the locations and surrounding lines of all TODOs, FIXMEs, and NOTEs in the codebase,
use the `notes.sh` script included with this project.

This project is free software, please refer to our [LICENSE](https://github.com/underground-software/RPi.GPIO2/blob/master/LICENSE.txt)
for further detail.

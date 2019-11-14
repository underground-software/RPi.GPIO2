#
# RPi.GPIO compatibility layer for libgpiod...
#
Summary: libgpiod compatibility layer for RPi.GPIO
Name: python3-libgpiod-rpi
Version: 1.0
Release: 1
License: GPLv3
#Group: 
Source: https://github.com/underground-software/libgpiod-rpi
#URL: http://www.gnomovision.com/cdplayer/cdplayer.html
Distribution: Fedora 30 Linux
Packager: UML Fedora RPI <fedora-rpi@googlegroups.com>
Requires: libgpiod-python


%description
This project implements a compatibility layer between RPi.GPIO syntax and libgpiod semantics.

%prep
%autosetup
rm -rf $RPM_BUILD_DIR/python3-libgpiod-rpi
tar xf $RPM_SOURCE_DIR/python3-libgpiod-rpi.tar.gz

%install
cp $RPM_SOURCE_DIR/* /usr/lib64/python3.7/site-packages

%files
%license LICENSE
%doc README.md
%{python3_sitearch}/gpiod-rpi/
 

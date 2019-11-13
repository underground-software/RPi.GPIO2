#
# RPi.GPIO compatibility layer for libgpiod...
#
Summary: libgpiod compatibility layer for RPi.GPIO
Name: python3-libgpiod-rpi
Version: 1.0
Release: 1
License: GPLv3
#Group: 
#Source: ftp://ftp.gnomovision.com/pub/cdplayer/cdplayer-1.0.tgz
#URL: http://www.gnomovision.com/cdplayer/cdplayer.html
Distribution: Fedora 30 Linux
Packager: UML Fedora RPI <fedora-rpi@googlegroups.com>

%description
This project implements a compatibility layer between RPi.GPIO syntax and libgpiod semantics.

%prep
rm -rf $RPM_BUILD_DIR/python3-libgpiod-rpi
tar xf $RPM_SOURCE_DIR/python3-libgpiod-rpi.tar.gz

%build

 

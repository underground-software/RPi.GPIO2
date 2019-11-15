#
# RPi.GPIO compatibility layer for libgpiod
#

Summary: libgpiod compatibility layer for RPi.GPIO
Name: python3-libgpiod-rpi
Version: 0.1
Release: 1
License: GPLv3
Source: https://github.com/underground-software/%{name}/archive/v%{version}.tar.gz
Distribution: Fedora 30 Linux
Packager: UML Fedora RPI <fedora-rpi@googlegroups.com>
Requires: python3
Requires: python3-libgpiod
Requires: bash

%define debug_package %{nil}

%description
This project implements a compatibility layer between RPi.GPIO syntax and libgpiod semantics.

%prep
#unzip $RPM_SOURCE_DIR/python3-libgpiod-rpi.zip
%setup

%build
# NOP

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{python3_sitearch}
cp -r RPi %{buildroot}/%{python3_sitearch}

%files
%license LICENSE
%doc README.md
%{python3_sitearch}/RPi

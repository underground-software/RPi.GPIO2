#
# RPi.GPIO compatibility layer for libgpiod
#

Summary: libgpiod compatibility layer for RPi.GPIO API
Name: python3-libgpiod-rpi
Version: 0.3.0
Release: 1%{?dist}
License: GPLv3
URL: https://python3-libgpiod-rpi.underground.software/%{name}
Source: https://github.com/underground-software/%{name}/archive/v%{version}.tar.gz
Requires: python3-libgpiod = 1.5.1
BuildArch: noarch

%define debug_package %{nil}

%description
This project implements a compatibility layer between RPi.GPIO syntax and libgpiod semantics.

%prep
# NOP

%setup
# NOP

%build
# NOP

%install
%py3_install

%files
%license LICENSE.md
%doc README.md
%{python3_sitearch}/RPi

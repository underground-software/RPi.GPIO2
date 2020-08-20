#
# RPi.GPIO compatibility layer for libgpiod
#

Summary: libgpiod compatibility layer for RPi.GPIO API
Name: python3-libgpiod-rpi
Version: 0.3.0
Release: 1%{?dist}
License: GPLv3+
URL: https://python3-libgpiod-rpi.underground.software/%{name}
Source: https://github.com/underground-software/%{name}/archive/v%{version}.tar.gz
# This explicity dependency on the libgpiod python bindings subpackage
# is neccessary because it is unsatisfiable via PyPi
Requires: python3-libgpiod >= 1.5
BuildArch: noarch

%define debug_package %{nil}

%description
This project implements a compatibility layer between RPi.GPIO syntax and
libgpiod semantics, allowing a fedora user on the Raspberry Pi platform to
use the popular RPi.GPIO API, the original implmenetation of which depends
on features provided by a non-mainline kernel.

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


%changelog
* Wed Aug 19 2020 Joel Savitz <joelsavitz@gmail.com> - 0.3.0-1
- initial package

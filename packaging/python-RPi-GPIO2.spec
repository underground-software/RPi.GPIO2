# python-RPi-GPIO2.spec
%global pypi_name	RPi.GPIO2

Summary: libgpiod compatibility layer for RPi.GPIO API
Name: python-RPi-GPIO2
Version: 0.3.0
Release: 1%{?dist}
License: GPLv3+
URL: https://python3-libgpiod-rpi.underground.software/
Source: ${pypi_source %pypi_name 0.3.0a3}

BuildRequires: python3-devel
BuildRequires: python3-setuptools

# This explicity dependency on the libgpiod python bindings subpackage
# is neccessary because it is unsatisfiable via PyPi
Requires: python3-libgpiod >= 1.5
BuildArch: noarch

%description
This library implements a compatibility layer between RPi.GPIO syntax and
libgpiod semantics, allowing a fedora user on the Raspberry Pi platform to
use the popular RPi.GPIO API, the original implmenetation of which depends
on features provided by a non-mainline kernel.

%prep
%autosetup -n ${srcname}-%{version}

%build
%py3_build

%install
%py3_install

%files
%license LICENSE.md
%doc README.md
%{python3_sitelib}/RPi/


%changelog
* Wed Aug 19 2020 Joel Savitz <joelsavitz@gmail.com> - 0.3.0-1
- initial package

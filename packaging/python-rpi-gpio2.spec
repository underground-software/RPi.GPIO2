Summary: A libgpiod compatibility layer for the RPi.GPIO API
Name: python-rpi-gpio2
Version: 0.4.0
Release: 1%{?dist}

License: GPL-3.0-or-later
URL: https://github.com/underground-software/RPi.GPIO2
Source0: %{url}/archive/v%{version}/RPi.GPIO2-%{version}.tar.gz

BuildArch: noarch
%global _description %{expand:
This library implements a compatibility layer between RPi.GPIO syntax and
libgpiod semantics, allowing a fedora user on the Raspberry Pi platform to
use the popular RPi.GPIO API, the original implementation of which depends
on features provided by a non-mainline kernel.}

%description %_description

%package -n python3-RPi.GPIO2
Summary: %{summary}

Obsoletes: python3-RPi.GPIO < 0.7.0-7
Provides: python3-RPi.GPIO = 1:%{version}-%{release}

BuildRequires: python3-devel
BuildRequires: python3-setuptools

# This explicit dependency on the libgpiod python bindings subpackage
# is neccessary because it is unsatisfiable via PyPi
Requires: python3-libgpiod >= 1.5

%description -n python3-RPi.GPIO2  %_description

%package doc
Summary: Examples for python-rpi-gpio2

%description doc
A set of examples for python-rpi-gpio2


%prep
%autosetup -n RPi.GPIO2-%{version}

# Make sure scripts in the examples directory aren't executable
chmod 0644 examples/*


%build
%py3_build

%install
%py3_install
rm -rf %{buildroot}%{python3_sitelib}/tests
rm -rf %{buildroot}%{python3_sitelib}/examples

%check
%py3_check_import RPi

# The tests rely on the presence of the actual physical GPIO pins on the system for now and though we may develop emulation functionality to run the tests on any system in the future we think the software is ready to be packaged as-is and we will just update it when the better tests are done


%files -n python3-RPi.GPIO2
%license LICENSE.txt
%doc README.md
%{python3_sitelib}/RPi/
%{python3_sitelib}/RPi.GPIO2-%{version}-py%{python3_version}.egg-info

%files doc
%license LICENSE.txt
%doc examples

%changelog
* Wed Aug 31 2022 Joel Savitz <joelsavitz@gmail.com> - 0.4.0-1
- initial package

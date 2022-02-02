# python-RPi-GPIO.spec
%global pkgname rpi-gpio2
%global pypi_name RPi.GPIO2

Summary: A libgpiod compatibility layer for the RPi.GPIO API
Name: python-%{pkgname}
Version: 0.3.0a3
Release: 1%{?dist}
License: GPLv3+
URL: https://github.com/underground-software/%{pypi_name}
Source0: %{url}/archive/v%{version}/%{pypi_name}-%{version}.tar.gz

Obsoletes: python-rpi-gpio = %{version}-%{release}
Provides: python-rpi-gpio

BuildArch: noarch
%global _description %{expand:
This library implements a compatibility layer between RPi.GPIO syntax and
libgpiod semantics, allowing a fedora user on the Raspberry Pi platform to
use the popular RPi.GPIO API, the original implementation of which depends
on features provided by a non-mainline kernel.}

%description %_description

%package -n python3-%{pypi_name}
Summary: %{summary}

Obsoletes: python3-RPi.GPIO <= 0.7.1
Provides: python3-RPi.GPIO = %{version}-%{release}

BuildRequires: python3-devel
BuildRequires: python3-setuptools

Recommends: python-%{pkgname}-doc

# This explicit dependency on the libgpiod python bindings subpackage
# is neccessary because it is unsatisfiable via PyPi
Requires: python3-libgpiod >= 1.5

%description -n python3-%{pypi_name}  %_description

%package doc
Summary: Examples for python-rpi-gpio2
%description doc
A set of examples for python-rpi-gpio2


%prep
%autosetup -n %{pypi_name}-%{version}

# Make sure scripts in the examples directory aren't executable
chmod 0644 examples/*


%build
%py3_build

%check
%py3_check_import RPi

# the tests rely on  the presence of the actual physical GPIO pins on the system for now and though we may develop emulation functionality to run the tests on any system in the future we think the software is ready to be packaged as-is and we will just update it when the better tests are done

%install
%py3_install
rm -rf %{buildroot}%{python3_sitelib}/tests
rm -rf %{buildroot}%{python3_sitelib}/examples

%files -n python3-%{pypi_name}
%license LICENSE.txt
%doc README.md
%{python3_sitelib}/RPi/
%{python3_sitelib}/%{pypi_name}-%{version}-py%{python3_version}.egg-info

%files doc
%license LICENSE.txt
%doc examples

%changelog
* Fri Jan 21 2022 Joel Savitz, Mwesigwa Guma <joelsavitz@gmail.com> <mguma@redhat.com> - 0.3.0a3-1
- initial package

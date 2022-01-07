# python-RPi-GPIO.spec
%global pkgname RPi.GPIO2

Summary: A libgpiod compatibility layer for the RPi.GPIO API
Name: python-rpi-gpio2
Version: 0.3.0a3
Release: 1%{?dist}
License: GPLv3+
URL: https://pypi.org/project/RPi.GPIO2/
Source0: https://github.com/underground-software/%{pkgname}/archive/v%{version}/%{pkgname}-%{version}.tar.gz

Obsoletes: python-rpi-gpio <= 0.7.1
Provides: python-rpi-gpio

BuildArch: noarch
%global _description %{expand:
This library implements a compatibility layer between RPi.GPIO syntax and
libgpiod semantics, allowing a fedora user on the Raspberry Pi platform to
use the popular RPi.GPIO API, the original implementation of which depends
on features provided by a non-mainline kernel.}

%description %_description

%package -n python3-%{pkgname}
Summary: %{summary}

Obsoletes: python3-RPi.GPIO <= 0.7.1
Provides: python3-RPi.GPIO = %{version}-%{release}

BuildRequires: python3-devel
BuildRequires: python3-setuptools

Recommends: python-%{pkgname}-doc

# This explicit dependency on the libgpiod python bindings subpackage
# is neccessary because it is unsatisfiable via PyPi
Requires: python3-libgpiod >= 1.5

%description -n python3-%{pkgname}  %_description

%package doc
Summary: Examples for python-rpi-gpio2
%description doc
A set of examples for python-rpi-gpio2


%prep
%autosetup -n %{pkgname}-%{version}

# Make sure scripts in the examples directory aren't executable
chmod 0644 examples/*


%build
%py3_build

%install
%py3_install
rm -rf %{buildroot}%{python3_sitelib}/tests
rm -rf %{buildroot}%{python3_sitelib}/examples

%files -n python3-%{pkgname}
%license LICENSE.txt
%doc README.md
%{python3_sitelib}/RPi/
%{python3_sitelib}/%{pkgname}-%{version}-py%{python3_version}.egg-info

%files doc
%license LICENSE.txt
%doc examples

%changelog
* Wed Aug 19 2020 Joel Savitz <joelsavitz@gmail.com> - 0.3.0a3-1
- initial package

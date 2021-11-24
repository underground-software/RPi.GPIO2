# python-RPi-GPIO2.spec
%global pypi_name RPi.GPIO2

Summary: A libgpiod compatibility layer for the RPi.GPIO API
Name: python-rpi-gpio2
Version: 0.3.0
Release: 1.a3%{?dist}
License: GPLv3+
URL: https://pypi.org/project/RPi.GPIO2/
Source0: https://github.com/underground-software/%{pypi_name}/archive/v%{version}a3/%{pypi_name}-%{version}a3.tar.gz

Obsoletes: python-rpi-gpio <= 0.7.1
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
Provides: python3-RPi.GPIO

BuildRequires: python3-devel
BuildRequires: python3-setuptools
%{?python_provide:%python_provide python3-%{pypi_name}}

# This explicit dependency on the libgpiod python bindings subpackage
# is neccessary because it is unsatisfiable via PyPi
Requires: python3-libgpiod >= 1.5


%description -n python3-%{pypi_name} %_description

%package -n python-%{pypi_name}-doc
Summary: Examples for python-rpi-gpio2
%description -n python-%{pypi_name}-doc
A set of examples for python-rpi-gpio2


%prep
%autosetup -n %{pypi_name}-%{version}a3

# Make sure scripts in the examples directory aren't executable
chmod 0644 examples/*


%build
%py3_build

%install
%py3_install
rm -rf %{buildroot}%{python3_sitelib}/tests
mkdir -p %{buildroot}%_pkgdocdir
cp -r %{buildroot}%{python3_sitelib}/examples %{buildroot}%_pkgdocdir
rm -rf %{buildroot}%{python3_sitelib}/examples

%files -n python3-%{pypi_name}
%license LICENSE.txt
%doc README.md
%{python3_sitelib}/RPi/
%{python3_sitelib}/%{pypi_name}-%{version}a3-py%{python3_version}.egg-info

%files -n python-%{pypi_name}-doc
%license LICENSE.txt
%_pkgdocdir/examples

%changelog
* Wed Aug 19 2020 Joel Savitz <joelsavitz@gmail.com> - 0.3.0-1.a3
- initial package

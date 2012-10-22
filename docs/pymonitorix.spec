#	@(#) Fibranet NSP, SL
#	Copyright (C) 2009 by Jordi Sanfeliu <jordi@fibranet.cat>
#
#	rpm spec for pyMonitorix
#

%define python_sitelib %(%{__python} -c 'from distutils import sysconfig; print sysconfig.get_python_lib()')

Summary: A PyGTK applet frontend for Monitorix
Name: pymonitorix
Version: 0.1.0
Release: 1%{?dist}
License: GPL
Group: Applications/System
URL: http://www.monitorix.org
Distribution: RedHat/Fedora/CentOS Linux
Vendor: Fibranet NSP, SL
Packager: Jordi Sanfeliu <jordi@fibranet.cat>

Source: %{name}-%{version}.tar.gz
BuildRequires: python >= 2.4 python-devel >= 2.4
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
Requires: python >= 2.4

%description
pyMonitorix is an applet application written in Python for the GNOME desktop,
it acts as the frontend of the Monitorix application installed on a local or
remote server. It is useful for those that want to monitorize their servers
without having to keep up and running the browser for doing that.

%prep
%setup -n %{name}-%{version}

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install --root=%{buildroot} --record=INSTALLED_FILES

cat << EOF > %{buildroot}/%{python_sitelib}/pymonitorix/config.py
datadir="%{_datadir}"
EOF

%clean
%{__rm} -rf %{buildroot}

#%files -f INSTALLED_FILES
%files
%defattr(-, root, root, 0755)
%doc Changes AUTHORS COPYING README
%{_bindir}/pymonitorix
%{python_sitelib}/*
%{_datadir}/pixmaps/pymonitorix.png
%{_datadir}/pymonitorix/pymonitorix.glade
%{_datadir}/pymonitorix/pymonitorix128x128.png
%{_datadir}/pymonitorix/pymonitorix19x17.png
%{_datadir}/applications/pymonitorix.desktop
%{_datadir}/locale/*

%changelog
* Fri Sep 13 2009 Jordi Sanfeliu <jordi@fibranet.cat>
- Release 0.1.0.
- Initial release.
- All changes are described in the Changes file.

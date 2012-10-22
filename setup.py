# Python Distutils Setup file for pyMonitorix.
# Build and install with:
#
#    python setup.py install
#
# 2009-09-01 Jordi Sanfeliu <jordi@fibranet.cat>
# -*- coding: UTF-8 -*-

from distutils.core import setup
import sys,os

if sys.platform == "win32":
	import py2exe

setup(
	name = 'pymonitorix',
	version = '0.1.0',
	description = 'PyGTK-based Monitorix frontend',
	long_description = 'PyGTK-based Monitorix applet frontend',
	author = 'Jordi Sanfeliu',
	author_email = 'jordi@fibranet.cat',
	license = 'GPL',
	url = 'http://www.monitorix.org',
	keywords = 'Monitorix',
	packages = ['pymonitorix'],
	scripts = ['scripts/pymonitorix'],
	data_files = [
		('share/pixmaps',
			[ 'pymonitorix/pymonitorix.png' ]
		),
		('share/pymonitorix',
			[
				'pymonitorix/pymonitorix.glade',
				'pymonitorix/pymonitorix128x128.png',
				'pymonitorix/pymonitorix19x17.png'
			]
		),
		('share/applications',
			[ 'pymonitorix.desktop' ]
		),
		('share/locale/ca/LC_MESSAGES', ['locale/ca/pymonitorix.mo']),
		('share/locale/de/LC_MESSAGES', ['locale/de/pymonitorix.mo']),
		('share/locale/en/LC_MESSAGES', ['locale/en/pymonitorix.mo']),
		],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: X11 Applications :: GTK',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: POSIX',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python',
		'Topic :: System :: Networking'
		],
	)


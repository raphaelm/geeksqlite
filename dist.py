#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, os.path
import sys
if os.path.exists('/usr/lib/geeksqlite/'):
	interfacedir        = '/usr/lib/geeksqlite/interface'
elif os.path.exists(os.path.abspath(sys.argv[0])+'/interface'):
	interfacedir 		= os.path.dirname(os.path.abspath(sys.argv[0]))+'/interface'
else:
	interfacedir		= './interface'
	
if os.path.exists('/usr/share/locale/en/LC_MESSAGES/geeksqlite.mo'):
	langdir        = '/usr/share/locale/'
elif os.path.exists(os.path.abspath(sys.argv[0])+'/language'):
	langdir 		= os.path.dirname(os.path.abspath(sys.argv[0]))+'/language'
else:
	langdir		= './language'
	
languages			= ['de', 'en', 'eo']
possibleconfigfiles = [os.path.expanduser('~/.geeksqlite'), os.path.dirname(os.path.abspath(sys.argv[0]))+'/geeksqlite.conf', './geeksqlite.conf', '/etc/geeksqlite']

if os.path.exists('/usr/share/pixmaps/geeksqlite.xpm'):
	icon				= '/usr/share/pixmaps/geeksqlite.xpm'
elif os.path.exists(os.path.abspath(sys.argv[0])+'/geeksqlite.xpm'):
	icon				= os.path.abspath(sys.argv[0])+'/geeksqlite.xpm'
else:
	icon				= './geeksqlite.xpm'

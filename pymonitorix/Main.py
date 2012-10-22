#!/usr/bin/python

"""
Copyright (C) 2009 Jordi Sanfeliu

Licensed under the GNU General Public License Version 2

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 51
Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
Jordi Sanfeliu <jordi@fibranet.cat>
http://www.monitorix.org
"""

import sys
import os
import locale
import gettext
import pygtk
pygtk.require("2.0")

try:
	import gtk
	import gtk.glade
except:
	sys.exit(1)

import urllib
import htmllib
import formatter

_ = gettext.gettext

GRAPH_TITLE = { "CPU load average and memory usage"	: "cpu",
		"Global kernel usage"			: "kern",
		"Kernel usage per processor"		: "proc",
		"HP Core temperatures"			: "hptemp",
		"LM-Sensors and disk temperatures"	: "lmtemp",
		"Disk i/o activity and usage"		: "disk",
		"Network traffic and usage"		: "net",
		"Network services demand"		: "servu",
		"Network port traffic"			: "port",
		"Users using the system"		: "user",
		"Nginx statistics"			: "nginx",
		"Devices interrupt activity"		: "int" }

MONITORIX_ICON = "pymonitorix19x17.png"

class ParseIndex(htmllib.HTMLParser):
	def __init__(self, formatter):
		htmllib.HTMLParser.__init__(self, formatter)
		self.graph_found = False
		self.optg = []
		self.opt = []
	
	def start_select(self, attrs):
		for attr in attrs:
			if attr[1] == "graph":
				self.graph_found = True
	def start_optgroup(self, attrs):
		if self.graph_found:
			for attr in attrs:
				self.optg.append(attr[1])
	def start_option(self, attrs):
		if self.graph_found:
			for attr in attrs:
				if attr[1] != "all":
					self.opt.append(attr[1][1:])

	def get_optgroups(self):
		return self.optg
	def get_options(self):
		return self.opt

class Menu:
	def __init__(self, main, url, optgroups, options, when):
		pos = 0
		sep0 = False
		prev_url = None
		popupmenu = main.menu
		self.main = main
		allopts = []
		for item in popupmenu:
			if item.get_name() == "separator0":
				sep0 = True
			if item.get_name() == "separator1":
				break
			if sep0:
				prev_url = item
			pos = pos + 1

		if not sep0:
			# creates the menu separator
			menu_item = gtk.SeparatorMenuItem()
			menu_item.set_name("separator0")
			menu_item.show()
			popupmenu.insert(menu_item, pos)
			pos = pos + 1
		else:
			# removes the previous URL menu entry
			prev_url.remove_submenu()
			menu = prev_url.get_parent()
			menu.remove(prev_url)
			self.main.icon.set_tooltip(None)
			pos = pos - 1

		# creates new URL menu entry
		sm = gtk.Menu()
		url_item = gtk.ImageMenuItem(url)
		url_image = gtk.Image()
		url_image.set_from_file(os.path.join(self.main.file_path, MONITORIX_ICON))
		url_item.set_image(url_image)
		url_item.set_submenu(sm)
		url_item.show()
		popupmenu.insert(url_item, pos)
		self.main.icon.set_tooltip(url)

		# creates submenu options
		ritem_group = None
		menu_item = gtk.RadioMenuItem(ritem_group, "All graphs")
		menu_item.set_name("All graphs")
		menu_item.set_active(True)
		for o in optgroups:
			allopts.append(GRAPH_TITLE[o])
		menu_item.connect("activate", self.set_graph, url, allopts, when, options)
		menu_item.show()
		sm.append(menu_item)
		ritem_group = menu_item
		for o in optgroups:
			allopts = []
			allopts.append(GRAPH_TITLE[o])
			menu_item = gtk.RadioMenuItem(ritem_group, o)
			menu_item.set_name(o)
			menu_item.set_active(False)
			menu_item.connect("activate", self.set_graph, url, allopts, when, options)
			menu_item.show()
			sm.append(menu_item)
		return

	def set_graph(self, widget, url, graph, when, options):
		if not widget.get_active():
			return False
		pngs = []
		data = urllib.urlencode({"mode" : "localhost",
					"graph" : graph,
					"when"  : when,
					"color" : "black" })
		pos = url[7:].find('/')
		urlhost = url
		if pos > 0:
			urlhost = url[:(7 + pos)]

		urlcgi = urlhost + "/cgi-bin/monitorix.cgi?"
		f = urllib.urlopen(urlcgi, data)
		f.read()

		self.main.wingraph.destroy()
		self.main.wingraph.set_title(widget.get_name())
		self.main.wingraph.set_icon_from_file(os.path.join(self.main.file_path, MONITORIX_ICON))
		self.main.wingraph.connect("delete_event", self.main.do_graph)
		global_vbox = gtk.VBox(False, 0)
		self.main.wingraph.add(global_vbox)

		for g in graph:
			pngs = []
			if g == "cpu"		or \
		   	   g == "kern"		or \
		   	   g == "hptemp"	or \
		   	   g == "lmtemp"	or \
		   	   g == "disk"		or \
		   	   g == "net"		or \
		   	   g == "servu"		or \
		   	   g == "user"		or \
		   	   g == "nginx"		or \
		   	   g == "int" :
				layout = 3
			elif g == "proc":
				layout = 2
			elif g == "port":
				layout = 6

			for o in options:
				if o[:len(g)] == g:
					pngs.append(o + "." + when + ".png")

			self.show_graph(widget, global_vbox, url, pngs, layout)

		self.main.wingraph.set_gravity(gtk.gdk.GRAVITY_NORTH_EAST)
		width, height = self.main.wingraph.get_size()
		self.main.wingraph.move(gtk.gdk.screen_width() - width, 0)
		self.main.wingraph.show_all()
		self.main.wingraph_stat = True
		return True

	def show_graph(self, widget, global_vbox, url, pngs, layout):
		img = []
		n = 0
		for png in pngs:
			file = urllib.urlopen(url + "/imgs/" + png)
			if file.headers.get("Content-Type") == "image/png":
				img.append(file.read())
				file.close()

		if layout == 2:
			hbox = gtk.HBox(False, 0)
			vbox = gtk.VBox(False, 0)
			for i in img:
				pbl = gtk.gdk.PixbufLoader('png')
				pbl.write(i)
				pbuf = pbl.get_pixbuf()
				pbl.close()
				image = gtk.Image()
				image.set_from_pixbuf(pbuf)
				hbox.add(image)
				n = n + 1
				if n % layout == 0:
					vbox.add(hbox)
					hbox = gtk.HBox(False, 0)
			global_vbox.add(vbox)

		if layout == 3:
			for i in img:
				if n % layout == 0:
					hbox = gtk.HBox(False, 0)
					vbox = gtk.VBox(False, 0)
					if n == 0 and len(img) < layout:
						vbox.set_homogeneous(True)
					pbl = gtk.gdk.PixbufLoader('png')
					pbl.write(i)
					pbuf = pbl.get_pixbuf()
					pbl.close()
					image = gtk.Image()
					image.set_from_pixbuf(pbuf)
					hbox.add(image)
					n = n + 1
					continue

				pbl = gtk.gdk.PixbufLoader('png')
				pbl.write(i)
				pbuf = pbl.get_pixbuf()
				pbl.close()
				image = gtk.Image()
				image.set_from_pixbuf(pbuf)
				vbox.add(image)
				valign = gtk.Alignment(0, 0, 0, 0)
				vbox.pack_start(valign)
				n = n + 1
				if n % layout == 0:
					hbox.add(vbox)
					vbox2 = gtk.VBox(False, 0)
					vbox2.add(hbox)
					global_vbox.add(vbox2)

			if n < layout:
				hbox.add(vbox)
				vbox2 = gtk.VBox(False, 0)
				vbox2.add(hbox)
				global_vbox.add(vbox2)

		if layout == 6:
			hbox = gtk.HBox(False, 0)
			vbox = gtk.VBox(False, 0)
			for i in img:
				pbl = gtk.gdk.PixbufLoader('png')
				pbl.write(i)
				pbuf = pbl.get_pixbuf()
				pbl.close()
				image = gtk.Image()
				image.set_from_pixbuf(pbuf)
				hbox.add(image)
				n = n + 1
				if n % 3 == 0:
					vbox.add(hbox)
					hbox = gtk.HBox(False, 0)
			global_vbox.add(vbox)

		return True

class Main:
	def __init__(self, datadir):
		APP = "pymonitorix"
		DIR = datadir + "/locale"
		gettext.bindtextdomain(APP, DIR)
		gettext.textdomain(APP)
		gtk.glade.bindtextdomain(APP, DIR)
		gtk.glade.textdomain(APP)
		_ = gettext.gettext

		self.file_path = datadir + "/pymonitorix"
		self.glade = gtk.glade.XML(os.path.join(self.file_path, "pymonitorix.glade"))
		dic = { "do_quit" : self.do_quit,
			"do_openurl_open" : self.do_openurl_open,
			"do_openurl_cancel" : self.do_openurl_cancel,
			"do_openurl_ok" : self.do_openurl_ok,
			"do_about_open" : self.do_about_open,
			"do_about_close" : self.do_about_close }
		self.glade.signal_autoconnect(dic)

		self.icon = gtk.StatusIcon()
		self.icon.set_from_file(os.path.join(self.file_path, MONITORIX_ICON))
		self.icon.connect("popup-menu", self.do_popup_menu)
		self.icon.connect("activate", self.do_graph)
		self.icon.set_visible(True)

		self.menu = self.glade.get_widget("popupmenu")

		self.openurl = self.glade.get_widget("openurlwin")
		self.openurl.connect("delete_event", self.do_openurl_cancel)

		self.aboutdialog = self.glade.get_widget("aboutdialog")
		self.aboutdialog.connect("delete_event", self.do_about_close)

		self.wingraph = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.wingraph_stat = False

	def do_popup_menu(self, icon, button, time):
#		gtk.gdk.beep()
		self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)

	def do_openurl_open(self, widget):
		focus = self.glade.get_widget("entry1")
		self.openurl.set_focus(focus)
		self.openurl.show()
	def do_openurl_cancel(self, *args):
		self.openurl.hide()
		return True
	def do_openurl_ok(self, widget):
		url = self.glade.get_widget("entry1").get_text()
		when = "day"
		if url == "":
			dialog = gtk.MessageDialog(self.openurl,
					flags=gtk.DIALOG_DESTROY_WITH_PARENT,
					type=gtk.MESSAGE_ERROR,
					buttons=gtk.BUTTONS_CLOSE,
					message_format="Error")
			dialog.format_secondary_text(_("Invalid URL."))
			dialog.run()
			dialog.destroy()
			return True
		try:
			f = urllib.urlopen(url)
			result = f.read()
		except IOError, e:
			estr = "%s" % e
			dialog = gtk.MessageDialog(self.openurl,
					flags=gtk.DIALOG_DESTROY_WITH_PARENT,
					type=gtk.MESSAGE_ERROR,
					buttons=gtk.BUTTONS_CLOSE,
					message_format="Error")
			dialog.format_secondary_text(estr)
			dialog.run()
			dialog.destroy()
			return True
		format = formatter.NullFormatter()
		htmlparser = ParseIndex(format)
		htmlparser.feed(result)
		htmlparser.close()
		optgroups = htmlparser.get_optgroups()
		options = htmlparser.get_options()
		if optgroups:
			if self.glade.get_widget("radiobutton1").get_active():
				when = "day"
			elif self.glade.get_widget("radiobutton2").get_active():
				when = "week"
			elif self.glade.get_widget("radiobutton3").get_active():
				when = "month"
			elif self.glade.get_widget("radiobutton4").get_active():
				when = "year"
			Menu(self, url, optgroups, options, when)
			self.openurl.hide()
			self.wingraph.destroy()
			self.wingraph.set_title("")
		else:
			text = _("Unable to retrieve Monitorix related information.")
			dialog = gtk.MessageDialog(self.openurl,
					flags=gtk.DIALOG_DESTROY_WITH_PARENT,
					type=gtk.MESSAGE_ERROR,
					buttons=gtk.BUTTONS_CLOSE,
					message_format="Error")
			dialog.format_secondary_text(text)
			dialog.run()
			dialog.destroy()
		return True

	def do_about_open(self, widget):
		self.aboutdialog.set_version("0.1.0")
		self.aboutdialog.show()
	def do_about_close(self, *args):
		self.aboutdialog.hide()
		return True

	def do_graph(self, *args):
		if self.wingraph.get_title() > "":
			if not self.wingraph_stat:
				self.wingraph.show_all()
			else:
				self.wingraph.hide_all()
			self.wingraph_stat = not self.wingraph_stat
		return True

	def do_quit(self, widget):
		gtk.main_quit()

	def main(self):
		gtk.main()

"""
	def do_preferences(widget, data = None):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_title("Preferences")
		window.connect("delete_event", window.destroy)
		window.show_all()
		window.run()
		window.destroy()
"""

if __name__ == "__main__":
	Main().main()


#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
try:
	import gtk, gtk.glade
	gtktype = "gtk"
except:
	print "Missing module PyGTK (v2)"
	sys.exit(1)

try:
	import gettext
except:
	print "Missing module gettext"
	sys.exit(1)

try:
	import sqlite3
except:
	print "Missing module SQLite3"
	sys.exit(1)
	
# Load Modules
import dist
import filedialog, os, ConfigParser, locale, re, math
from optparse import OptionParser

# Load config
def loadconfig():
	global cfgfilename, cfgfile, config, LANGUAGE, ENCODING
	cfgfilename = ''
	for n in dist.possibleconfigfiles:
		if os.path.isfile(n):
			cfgfilename = n
			print "Load configuration from: "+n
			break
		else:
			try:
				open(n, 'a+') # Create file
				if os.access(n, os.W_OK):
					cfgfilename = n
					print "Create new config file: "+n
					break
			except:
				a = 0
	loadconfigfile(cfgfilename)
	
def loadconfigfile(cfgfilename):
	global cfgfile, config, LANGUAGE, ENCODING, CSVSEP, CSVMASK
	try:
		config = ConfigParser.ConfigParser()
		config.read(cfgfilename)
		# Load Config, set defaults
		try:
			config.add_section('locale')
		except:
			pass
		try:
			config.add_section('export')
		except:
			pass
		try:
			LANGUAGE = config.get('locale', 'lang').strip()
		except:
			LANGUAGE = 'en'
		try:
			CSVSEP = config.get('export', 'csvsep').strip()
		except:
			CSVSEP = ','
		try:
			CSVMASK = config.get('export', 'csvmask').strip()
			if CSVMASK != 'True':
				CSVMASK = False
			else:
				CSVMASK = True
		except:
			CSVMASK = True
		try:
			ENCODING = config.get('locale', 'encoding').strip()
		except:
			ENCODING = 'utf-8'
		locale.setlocale(locale.LC_ALL, (LANGUAGE, ENCODING))
	except:
		print "Failed loading configuration"
	
try:
	gtk.glade.bindtextdomain('geeksqlite', dist.langdir)
	gtk.glade.textdomain('geeksqlite')
	gettext.bindtextdomain('geeksqlite', dist.langdir)
	gettext.textdomain('geeksqlite')
	_ = gettext.gettext
except:
	print "Failed loading language"
	
# Cersion Information
ver_name 			= _("geek'SQLite")
ver_version			= "0.0.0"
ver_copyright		= _(u"Copyright © 2010 geek's factory")
ver_comments		= _("free Python GTK+ SQLite3 database file browser")
ver_license			= _("""Copyright (c) 2010 geek's factory

MIT-License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.""")
ver_website			= "http://www.geeksfactory.de/geeksqlite"
ver_website_label	= "geeksfactory.de/geeksqlite"
# Add you here if you have edited the code, the documentation or 
# something else
ver_authors			= ["Raphael Michel <raphael@geeksfactory.de>"]
ver_documenters		= ["Raphael Michel <raphael@geeksfactory.de>"]
ver_artists			= ["Raphael Michel <raphael@geeksfactory.de>"]

def ver_translators(language):
	if language == 'en':
		return """Raphael Michel <raphael@geeksfactory.de>"""
	elif language == 'de':
		return """Raphael Michel <raphael@geeksfactory.de>"""
	elif language == 'eo':
		return u"""Nils Martin Klünder <webmaster@nomoketo.de>"""

# GTK HELPERS

def err(text):
	error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR
				, message_format=text
				, buttons=gtk.BUTTONS_OK)
	error_dlg.run()
	error_dlg.destroy()

def warning(text):
	error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_WARNING
				, message_format=text
				, buttons=gtk.BUTTONS_OK)
	error_dlg.run()
	error_dlg.destroy()

def info(text):
	error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO
				, message_format=text
				, buttons=gtk.BUTTONS_OK)
	error_dlg.run()
	error_dlg.destroy()
	
def confirm(text):
	dlg = gtk.MessageDialog(message_format=text, 
							flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
							type=gtk.MESSAGE_QUESTION)
	dlg.add_button(gtk.STOCK_NO, 1)
	dlg.add_button(gtk.STOCK_YES, 3)
	run = dlg.run()
	if run == 3:
		ret = True
	else:
		ret = False
	dlg.destroy()
	return ret
	
def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def sqlerr(query, error):
	
	dlg = gtk.MessageDialog(flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
							type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
							message_format=_('An error occured while executing a SQL database query!'))
	dlg.format_secondary_markup(
		_('SQL query which caused the error:\n\n<tt>%(query)s</tt>\n\nSQLite error message:\n\n<tt>%(error)s</tt>') % 
		{
			'query': wrap(query, 80),
			'error': wrap(error, 80)
		})
	dlg.set_title(_('SQL error'))
	
	run = dlg.run()
	dlg.destroy()
	
# SUB CLASSES
class TableCreator:
	def add(self):
		dialogTree = gtk.glade.XML(dist.interfacedir+"/addfielddialog.glade")
		dlg = dialogTree.get_widget('AddFieldDialog')
		
		cb = gtk.combo_box_new_text()
		cb.set_size_request(195,30)
		cb.append_text('TEXT')
		cb.append_text('NUMERIC')
		cb.append_text('INTEGER PRIMARY KEY')
		cb.append_text('BLOB')
		cb.show()
		dialogTree.get_widget('AddFieldField').put(cb, 115, 35)
		
		run = dlg.run()
		if run == 3:
			if cb.get_active_text():
				ftype = cb.get_active_text()
			else:
				ftype = ''
			
			if dialogTree.get_widget('RadioNOTNULL').get_active():
				ftype += ' NOT NULL'
			elif dialogTree.get_widget('RadioUNIQUE').get_active():
				ftype += ' UNIQUE'
			elif dialogTree.get_widget('RadioDEFAULT').get_active():
				ftype += ' DEFAULT \''+dialogTree.get_widget('DefaultInput').get_text()+'\''
				
			fname = dialogTree.get_widget('NameInput').get_text()
			dlg.destroy()
			self.ftv.get_model().append([fname, ftype])
		else:
			dlg.destroy()
			return False
		
	def delete(self):
		tuple = self.ftv.get_selection().get_selected()
		model = tuple[0]
		iter = tuple[1]
		if iter != None:
			del model[iter]
		
	def build_query(self, tblname):
		query = ['CREATE TABLE']
		query.append('`'+tblname+'`')
		fieldlistitems = []
		for row in self.ftv.get_model():
			fieldlistitems.append('`'+row[0]+'` '+row[1])
			
		if len(tblname) < 1 or len(fieldlistitems) < 1:
			return False
		
		fieldlist = '(' + ", ".join(fieldlistitems) + ')'
		query.append(fieldlist)
		
		return " ".join(query) + ";"
		
	def __init__(self):
		self.dialogTree = gtk.glade.XML(dist.interfacedir+"/tablecreatedialog.glade")
		self.dlg = self.dialogTree.get_widget('TableCreateDialog')
		
		self.dialogTree.get_widget('AddBtn').connect('activate', self.add)
		
		self.ftv = self.dialogTree.get_widget('FieldsTV')
		
		self.structtv_col = gtk.TreeViewColumn(_('Name'))
		self.structtv_cell = gtk.CellRendererText()
		self.structtv_col.pack_start(self.structtv_cell)
		self.structtv_col.add_attribute(self.structtv_cell, 'text', 0)
		self.structtv_col.set_resizable(True)
		self.structtv_col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		self.structtv_col.set_fixed_width(210)
		self.ftv.append_column(self.structtv_col)	
		
		self.structtv_col2 = gtk.TreeViewColumn(_('Type'))
		self.structtv_cell2 = gtk.CellRendererText()
		self.structtv_col2.pack_start(self.structtv_cell2)
		self.structtv_col2.add_attribute(self.structtv_cell2, 'text', 1)
		self.structtv_col2.set_resizable(True)
		self.structtv_col2.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		self.structtv_col2.set_fixed_width(210)
		self.ftv.append_column(self.structtv_col2)
		
		ls = gtk.ListStore(str, str)
		self.ftv.set_model(ls)	
	
	def run(self):
		self.runv = self.dlg.run()
		
		if self.runv == 6:
			self.add()
			return self.run()
		elif self.runv == 7:
			self.delete()
			return self.run()
		elif self.runv == 3:
			tblname = self.dialogTree.get_widget('TblNameEntry').get_text()
			result = self.build_query(tblname)
			if not result:
				err(_('Error while creating new table. Did you fill in all form fields? Did you add any fields to your table?'))
				return self.run()
			else:
				self.dlg.destroy()
				return result
		else:
			self.dlg.destroy()
			return False
			
class TableModifier(TableCreator):
		
	def build_query(self, tblname):
		queries = []
		
		# Rename Query
		queries.append("ALTER TABLE `"+self.oldtblname+"` RENAME TO `geeksqlite_tmp_table`")
		
		# Create Query
		query = ['CREATE TABLE']
		query.append('`'+tblname+'`')
		fieldlistitems = []
		for row in self.ftv.get_model():
			fieldlistitems.append('`'+row[0]+'` '+row[1])
			self.newfields.append(row[0])
			
		if len(tblname) < 1 or len(fieldlistitems) < 1:
			return False
		
		fieldlist = '(' + ", ".join(fieldlistitems) + ')'
		query.append(fieldlist)
		
		queries.append(" ".join(query) + ";")
		
		if self.newfields == self.oldfields and tblname == self.oldtblname:
			return []
		elif self.newfields == self.oldfields and tblname != self.oldtblname:
			return ["ALTER TABLE `"+self.oldtblname+"` RENAME TO `"+tblname+"`"]
		
		# Copy and Drop
		holdfields = list(set(self.oldfields) & set(self.newfields))
		holdfields = ", ".join(holdfields)
		queries.append("INSERT INTO `"+tblname+"` ("+holdfields+") SELECT "+holdfields+" FROM `geeksqlite_tmp_table`")
		queries.append("DROP TABLE `geeksqlite_tmp_table`")
		
		return queries
		
	def __init__(self, tblname, tblquery, geeksqlitem):
		
		self.oldtblname = tblname
		self.oldtblquery = tblquery
		self.newfields = []
		self.oldfields = []
		
		self.dialogTree = gtk.glade.XML(dist.interfacedir+"/tablemodifydialog.glade")
		self.dlg = self.dialogTree.get_widget('TableModifyDialog')
		
		self.dialogTree.get_widget('AddBtn').connect('activate', self.add)
		
		self.ftv = self.dialogTree.get_widget('FieldsTV')
		
		self.structtv_col = gtk.TreeViewColumn(_('Name'))
		self.structtv_cell = gtk.CellRendererText()
		self.structtv_col.pack_start(self.structtv_cell)
		self.structtv_col.add_attribute(self.structtv_cell, 'text', 0)
		self.structtv_col.set_resizable(True)
		self.structtv_col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		self.structtv_col.set_fixed_width(210)
		self.ftv.append_column(self.structtv_col)	
		
		self.structtv_col2 = gtk.TreeViewColumn(_('Type'))
		self.structtv_cell2 = gtk.CellRendererText()
		self.structtv_col2.pack_start(self.structtv_cell2)
		self.structtv_col2.add_attribute(self.structtv_cell2, 'text', 1)
		self.structtv_col2.set_resizable(True)
		self.structtv_col2.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		self.structtv_col2.set_fixed_width(210)
		self.ftv.append_column(self.structtv_col2)
		
		ls = gtk.ListStore(str, str)
		
		self.dialogTree.get_widget('TblNameEntry').set_text(self.oldtblname)
		
		m = re.search(r'CREATE TABLE ([^\(]*) \((.*)\)', tblquery)
		fields = m.group(2).strip().replace('`', '')
		if ',' in fields:
			fieldlist = fields.split(',')
			for f in fieldlist:
				f = f.strip()
				spacepos = f.find(' ')
				if spacepos == -1:
					ls.append([f, ''])
					self.oldfields.append(f)
				else:
					ls.append([f[:spacepos], f[spacepos:].strip()])
					self.oldfields.append(f[:spacepos])
		else:
			spacepos = fields.find(' ')
			if spacepos == -1:
				ls.append([fields, ''])
				self.oldfields.append(fields)
			else:
				ls.append([fields[:spacepos], fields[spacepos:].strip()])
				self.oldfields.append(fields[:spacepos])
							
		self.ftv.set_model(ls)	
	
	def run(self):
		self.runv = self.dlg.run()
		
		if self.runv == 6:
			self.add()
			return self.run()
		elif self.runv == 7:
			self.delete()
			return self.run()
		elif self.runv == 3:
			tblname = self.dialogTree.get_widget('TblNameEntry').get_text()
			result = self.build_query(tblname)
			if not result:
				err(_('Error while modifing table. Did you fill in all fields? Are there any fields in your new table?'))
				return self.run()
			else:
				self.dlg.destroy()
				return result
		else:
			self.dlg.destroy()
			return False
			
# MAIN CLASS
class geeksqliteMain:
	def gettablename(self, title):
		dialogTree = gtk.glade.XML(dist.interfacedir+"/tablenamedialog.glade")
		dlg = dialogTree.get_widget('TableNameDialog')
		dlg.set_title(title)
		
		cb = gtk.combo_box_new_text()
		cb.set_size_request(240,30)
		
		result = self.sql('select `name`, `sql` from `sqlite_master` WHERE `type` = "table";')
		for row in self.cursor:
			n = row[0]
			#ls.append([n])
			cb.append_text(n)
		
		cb.show()
		dialogTree.get_widget('TableNameField').put(cb, 5, 25)
		run = dlg.run()
		if run == 3:
			if cb.get_active_text():
				tablename = cb.get_active_text()
			else:
				tablename = None
			dlg.destroy()
			return tablename
		else:
			dlg.destroy()
			return None
	
	def getindexname(self, title):
		dialogTree = gtk.glade.XML(dist.interfacedir+"/indexnamedialog.glade")
		dlg = dialogTree.get_widget('TableNameDialog')
		dlg.set_title(title)
		
		cb = gtk.combo_box_new_text()
		cb.set_size_request(240,30)
		
		result = self.sql('select `name`, `sql` from `sqlite_master` WHERE `type` = "index";')
		for row in self.cursor:
			n = row[0]
			#ls.append([n])
			cb.append_text(n)
		
		cb.show()
		dialogTree.get_widget('IndexNameField').put(cb, 5, 25)
		run = dlg.run()
		if run == 3:
			if cb.get_active_text():
				tablename = cb.get_active_text()
			else:
				tablename = None
			dlg.destroy()
			return tablename
		else:
			dlg.destroy()
			return None
	
	def getviewname(self, title):
		dialogTree = gtk.glade.XML(dist.interfacedir+"/viewnamedialog.glade")
		dlg = dialogTree.get_widget('ViewNameDialog')
		dlg.set_title(title)
		
		cb = gtk.combo_box_new_text()
		cb.set_size_request(240,30)
		
		result = self.sql('select `name`, `sql` from `sqlite_master` WHERE `type` = "view";')
		for row in self.cursor:
			n = row[0]
			#ls.append([n])
			cb.append_text(n)
		
		cb.show()
		dialogTree.get_widget('ViewNameField').put(cb, 5, 25)
		run = dlg.run()
		if run == 3:
			if cb.get_active_text():
				tablename = cb.get_active_text()
			else:
				tablename = None
			dlg.destroy()
			return tablename
		else:
			dlg.destroy()
			return None
		
	def browse_to(self, table, start=0, limit=50, search=None):
		self.browse_current_table = table
		self.browse_current_start = start
		self.browse_current_limit = limit
		self.browse_current_search = search
		self.browse_current_count = 0
		
		if self.fileopened:
			ef = self.mainTree.get_widget('DataField')
			try:
				ef.remove(self.btv)
				self.btv = False
			except:
				self.btv = False
			try:
				query = "SELECT `_rowid_`, * FROM `"+table+"`";
				if search != None:
					query += " WHERE "+search
				query += " LIMIT "+str(start)+","+str(limit)+";"
				result = self.sql(query)
				ls = False
				C = 0
				any = False
				l = len(self.cursor.description)
				columns = [str] * l
				self.emptyrow = [None]*l
				ls = gtk.ListStore(*columns)
				for row in self.cursor:
					any = True
					list = []
					for field in row:
						if field == None:
							field = ''
						list.append(str(field))
					ls.append(list)
					C += 1
				if any:
					cols = [""]*l
					cells = [""]*l
					self.browse_current_labels = [""]*l
					j = 0
					for k in self.cursor.description:
						self.browse_current_labels[j] = str(k[0])
						j += 1
					self.btv = gtk.TreeView(ls)
					for i in range(0,l):
						if i == 0:
							coltitle = '#'
						else:
							coltitle = self.browse_current_labels[i]
						cols[i] = gtk.TreeViewColumn(coltitle)
						cells[i] = gtk.CellRendererText()
						cols[i].pack_start(cells[i])
						cols[i].add_attribute(cells[i], 'text', i)
						cols[i].set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
						cols[i].set_fixed_width(100)
						cells[i].set_property('editable', True)
						cells[i].connect('edited', self.edited, (i, ls))
						cols[i].set_resizable(True)
						self.btv.append_column(cols[i])
						self.btv.show()
					cols[0].set_fixed_width(45)
					ef.add(self.btv)
					self.browse_current_count = C
					self.refreshscrolllabel()
			except sqlite3.Error, e:
				err('[SQLite Error] '+e.args[0])
	
	def refreshscrolllabel(self):
		scrolllabel = self.mainTree.get_widget('ScrollLabel')
		allquery = "SELECT * FROM `"+self.browse_current_table+"`"
		if self.browse_current_search != None:
			allquery += " WHERE "+self.browse_current_search
		result2 = self.sql(allquery)
		total = len(self.cursor.fetchall())
		if total < self.browse_current_start+self.browse_current_limit:
			self.mainTree.get_widget('ScrollRight').hide()
		else:
			self.mainTree.get_widget('ScrollRight').show()
		if self.browse_current_start == 0:
			self.mainTree.get_widget('ScrollLeft').hide()
		else:
			self.mainTree.get_widget('ScrollLeft').show()
		scrolllabel.set_text(_('%(start)d to %(end)d of %(total)d') % {'start':self.browse_current_start+1, 'end':self.browse_current_start+self.browse_current_count, 'total':total})
		return total
	
	def do_open(self, file=None):
		if file != None:
			self.filename = file
		if self.filename:
			try:
				self.close()
				self.connection = sqlite3.connect(self.filename)
				self.cursor = self.connection.cursor()
				self.fileopened = True
				self.connection.text_factory = str
				self.cursor.execute('select `name`, `sql` from `sqlite_master` WHERE `type` = "table";')
				self.log_add(_('-- -- OPEN FILE -- --'))
			except:
				err(_('Unable to open database file'))
				self.fileopened = False
		self.reloadstructure()
		self.reloadbrowse()
				
	def log_add(self, text):
		buf = self.mainTree.get_widget('LogMemo').get_buffer()
		buf.insert(buf.get_end_iter(), text+"\n")
		
	def sql(self, text, parameters = None, errorhandling = True):
		self.log_add(text)
		if errorhandling == False: 
			if parameters:
				return self.cursor.execute(text, parameters)
			else:
				return self.cursor.execute(text)
		else:
			try:
				if parameters:
					return self.cursor.execute(text, parameters)
				else:
					return self.cursor.execute(text)
			except sqlite3.Error, e:
				if parameters != None:
					text += '\n-- Arguments: '+str(parameters)
				sqlerr(text, e.args[0])
				return False
			
		
	def reloadbrowse(self, this = None):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			self.browse_to(table=self.browse_current_table,
			start=self.browse_current_start,
			limit=self.browse_current_limit,
			search=self.browse_current_search)
		
	def reloadstructure(self):
		# Tables
		ls = gtk.ListStore(str, str, str)
		ls2 = gtk.ListStore(str)
		result = self.sql('select `name`, `sql` from `sqlite_master` WHERE `type` = "table";')
		for row in self.cursor:
			n = row[0]
			ls.append([n, _('table'), row[1]])
			ls2.append([n])
			
		# Indexes
		result = self.sql('select `name`, `sql` from `sqlite_master` WHERE `type` = "index";')
		for row in self.cursor:
			n = row[0]
			ls.append([n, _('index'), row[1]])
			
		# Views
		result = self.sql('select `name`, `sql` from `sqlite_master` WHERE `type` = "view";')
		for row in self.cursor:
			n = row[0]
			ls.append([n, _('view'), row[1]])
			ls2.append([n])
			
		self.mainTree.get_widget('StructTv').set_model(ls)
		self.mainTree.get_widget('TableSelect').set_model(ls2)
		
	def index_create(self, this):
		if self.fileopened:
			tblname = self.gettablename(_('Select Table'))
			if tblname:
				dialogTree = gtk.glade.XML(dist.interfacedir+"/indexcreatedialog.glade")
				dlg = dialogTree.get_widget('IndexCreateDialog')
		
				cb = gtk.combo_box_new_text()
				cb.set_size_request(295,30)
				dialogTree.get_widget('OrderSelect').set_active(0)
				
				res = self.sql("SELECT `sql` FROM `sqlite_master` WHERE `name` = '"+tblname+"'")
				row = self.cursor.fetchone()
				m = re.search(r'CREATE TABLE ([^\(]*) \((.*)\)', row[0])
				fields = m.group(2).strip().replace('`', '')
				if ',' in fields:
					fieldlist = fields.split(',')
					for f in fieldlist:
						f = f.strip()
						spacepos = f.find(' ')
						if spacepos == -1:
							cb.append_text(f)
						else:
							cb.append_text(f[:spacepos])
				else:
					spacepos = fields.find(' ')
					cb.append_text(fields[:spacepos])
				
				cb.show()
				dialogTree.get_widget('IndexCreateField').put(cb, 110, 40)
				run = dlg.run()
				if run == 3:
					if cb.get_active_text() and dialogTree.get_widget('OrderSelect').get_active_text() and dialogTree.get_widget('NameEntry').get_text():
						sql = "CREATE "
						if dialogTree.get_widget('UniqueCheck').get_active():
							sql += "UNIQUE "
						sql += "INDEX "
						sql += dialogTree.get_widget('NameEntry').get_text()
						sql += " ON `"
						sql += tblname
						sql += "` (`"
						sql += cb.get_active_text()
						sql += "` "
						order = dialogTree.get_widget('OrderSelect').get_active_text()
						sql += order[:order.find(' ')].strip()
						sql += ");"
						try:
							self.sql(sql)
							self.reloadstructure()
						except sqlite3.Error, e:
							err('[SQLite Error] '+e.args[0])
					else:
						warning(_('No index was created because you did not fill in all required fields!'))
					dlg.destroy()
				else:
					dlg.destroy()
					return None
		else:
			err(_('No database loaded'))
			
	def edited(self, cell, path, new_text, user_data):
		model = user_data[1]
		iter = model.get_iter(path)
		if iter != None:
				rowid = str(model.get(iter, 0)[0])
				if not self.sql('UPDATE `'+self.browse_current_table+'` SET `'+self.browse_current_labels[user_data[0]]+"` = ? WHERE `_rowid_` = ?", (new_text, rowid)):
					return False
				else:
					model[path][user_data[0]] = new_text
					return 
		
	def close(self, this = None):
		if self.fileopened:
			try:
				self.mainTree.get_widget('ExecField').remove(self.exectv)
			except:
				pass
			try:
				self.mainTree.get_widget('DataField').remove(self.btv)
			except:
				pass
			ls = gtk.ListStore(str, str, str)
			ls2 = gtk.ListStore(str)
			self.mainTree.get_widget('StructTv').set_model(ls)
			self.mainTree.get_widget('TableSelect').set_model(ls2)
			self.connection.commit()
			self.connection.close()
			self.cursor = None
			self.fileopened = False
			self.log_add(_('-- -- CLOSE FILE -- --'))
		else:
			self.fileopened = False
		
	def open(self, this):
		d = filedialog.FileDialog()
		self.filename = d.get_filename(action='open')
		self.do_open()
		
	def table_create(self, this):
		if self.fileopened:
			tc = TableCreator()
			result = tc.run()
			if result:
				self.sql(result)
				self.reloadstructure()
		else:
			err(_('No database loaded'))
		
	def table_modify(self, this):
		if self.fileopened:
			tblname = self.gettablename(_('Modify Table'))
			if tblname:
				result = self.sql('select `sql` from `sqlite_master` WHERE `type` = "table" AND `name` = ?;', (tblname,))
				tblquery = self.cursor.fetchone()[0]
				tc = TableModifier(tblname, tblquery, self)
				result = tc.run()
				if result:
					for q in result:
						if not self.sql(q):
							break
					self.reloadstructure()
		else:
			err(_('No database loaded'))
			
	def table_delete(self, this):
		if self.fileopened:
			tblname = self.gettablename(_('Drop Table'))
			if tblname and confirm(_("Do you really want to remove the table %s?") % tblname):
				self.sql('DROP TABLE IF EXISTS `'+tblname+'`')
				if tblname == self.browse_current_table:
					self.browse_to('sqlite_master',
					start=0,
					limit=0,
					search=None)
				self.reloadstructure()
		else:
			err(_('No database loaded'))
		
	def view_delete(self, this):
		if self.fileopened:
			tblname = self.getviewname(_('Drop View'))
			if tblname and confirm(_("Do you really want to remove the view %s?") % tblname):
				self.sql('DROP VIEW IF EXISTS `'+tblname+'`')
				if tblname == self.browse_current_table:
					self.browse_to('sqlite_master',
					start=0,
					limit=0,
					search=None)
				self.reloadstructure()
		else:
			err(_('No database loaded'))
		
	def view_create(self, this):
		if self.fileopened:
				dialogTree = gtk.glade.XML(dist.interfacedir+"/viewcreatedialog.glade")
				dlg = dialogTree.get_widget('CreateViewDialog')
		
				run = dlg.run()
				if run == 3:
					ibuf = dialogTree.get_widget('ViewSQL').get_buffer()
					inpu = ibuf.get_text(ibuf.get_start_iter(), ibuf.get_end_iter())
					if dialogTree.get_widget('ViewName').get_text() and len(inpu) > 0:
						sql = "CREATE VIEW `"
						sql += dialogTree.get_widget('ViewName').get_text()
						sql += "` AS "
						sql += inpu
						
						self.sql(sql)
						self.reloadstructure()
					else:
						warning(_('No view was created because you did not fill in all required fields!'))
					dlg.destroy()
				else:
					dlg.destroy()
					return None
		else:
			err(_('No database loaded'))
		
	def index_delete(self, this):
		if self.fileopened:
			indexname = self.getindexname(_('Drop Index'))
			if indexname and confirm(_("Do you really want to remove the index %s?") % indexname):
				self.sql('DROP INDEX IF EXISTS `'+indexname+'`')
				self.reloadbrowse()
				self.reloadstructure()
		else:
			err(_('No database loaded'))
		
	def exit(self, this = False):
		self.close()
		gtk.main_quit(self, this)
		sys.exit(0)
		
	def display_about(self, this): # About
		global LANGUAGE, ver_name, ver_name, ver_version, ver_copyright
		global ver_comments, ver_license, ver_website, ver_website_label
		global ver_authors, ver_documenters, ver_artists
		dialog = gtk.AboutDialog()
		dialog.set_name(ver_name)
		dialog.set_program_name(ver_name)
		dialog.set_version(ver_version)
		dialog.set_copyright(ver_copyright)
		dialog.set_comments(ver_comments)
		dialog.set_license(ver_license)
		dialog.set_website(ver_website)
		dialog.set_website_label(ver_website_label)
		dialog.set_authors(ver_authors)
		dialog.set_documenters(ver_documenters)
		dialog.set_artists(ver_artists)
		dialog.set_translator_credits(ver_translators(LANGUAGE))
		response = dialog.run()
		dialog.hide()
		
	def browse(self, this):
		if this.get_active_text() != None:
			self.browse_to(table=this.get_active_text(),start=0,limit=50,search=None)
		
	def browse_nextpage(self, this):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			self.browse_to(table=self.browse_current_table,
			start=self.browse_current_start+self.browse_current_limit,
			limit=self.browse_current_limit,
			search=self.browse_current_search)
		
	def browse_previouspage(self, this):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			start = self.browse_current_start-self.browse_current_limit
			if start < 0:
				start = 0
			self.browse_to(table=self.browse_current_table,
			start=start,
			limit=self.browse_current_limit,
			search=self.browse_current_search)

	def execute(self, this):
		if self.fileopened:
			ibuf = self.mainTree.get_widget('ExecInput').get_buffer()
			inpu = ibuf.get_text(ibuf.get_start_iter(), ibuf.get_end_iter())
			ebuf = self.mainTree.get_widget('ExecError').get_buffer()
			erro = ebuf.get_text(ebuf.get_start_iter(), ebuf.get_end_iter())
			ef = self.mainTree.get_widget('ExecField')
			if not inpu.rstrip().endswith(";"):
				inpu = inpu+';'
				ibuf.insert(ibuf.get_end_iter(), ';')
			if sqlite3.complete_statement(inpu):
				try:
					ef.remove(self.exectv)
					self.exectv = False
				except:
					pass
				try:
					result = self.sql(inpu, None, False)
					if inpu.lstrip().upper().startswith("SELECT"):
						ls = False
						i = 0
						for row in self.cursor:
							l = len(row)
							list = []
							for field in row:
								list.append(str(field))
							if not ls:
								columns = [str] * l
								ls = gtk.ListStore(*columns)
							ls.append(list)
							i += 1
						if i == 0:
							ebuf.set_text(_('Empty result'))
						else:
							cols = [""]*l
							cells = [""]*l
							labels = [""]*l
							j = 0
							for k in self.cursor.description:
								labels[j] = str(k[0])
								j += 1
							self.exectv = gtk.TreeView(ls)
							for i in range(0,l):
								cols[i] = gtk.TreeViewColumn(labels[i])
								cells[i] = gtk.CellRendererText()
								cols[i].pack_start(cells[i])
								cols[i].add_attribute(cells[i], 'text', i)
								cols[i].set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
								cols[i].set_fixed_width(100)
								cols[i].set_resizable(True)
								self.exectv.append_column(cols[i])
								self.exectv.show()
							ef.add(self.exectv)
					self.reloadstructure()
					self.reloadbrowse()
				except sqlite3.Error, e:
					ebuf.set_text(_('[SQLite Error] ')+e.args[0])
			else:
				ebuf.set_text(_('[geekSQLite Error] Not a complete statement!'))
		else:
			err(_('No database loaded'))
		
	def importSQL(self, this):
		if self.fileopened:
			d = filedialog.FileDialog()
			f = d.get_filename(action='open')
			if f != None:
				s = file(f).read()
				try:
					self.cursor.executescript(s)
				except sqlite3.Error, e:
					err('SQLite Error: '+e.args[0])
				self.connection.commit()
				self.reloadstructure()
				self.reloadbrowse()
		else:
			err(_('No database loaded'))
	
	def exportSQL(self, this):
		if self.fileopened:
			d = filedialog.FileDialog()
			f = d.get_filename(action='save')
			if f != None:
				s = file(f).read()
				with open(f, 'w') as f:
					for line in self.connection.iterdump():
						f.write('%s\n' % line)
		else:
			err(_('No database loaded'))
	
	def exportCSV(self, this):
		global CSVSEP, CSVMASK
		if self.fileopened:
			cb = self.mainTree.get_widget('TableSelect').get_active_text()
			if cb != None:
				d = filedialog.FileDialog()
				f = d.get_filename(action='save')
				if f != None:
					f = open(f, 'w+')
					
					search = self.browse_current_search
					query = "SELECT `_rowid_`, * FROM `"+cb+"`";
					if search != None:
						query += " WHERE "+search
					result = self.sql(query)
					
					labels = []
					for label in self.cursor.description:
						labels.append(label[0])
						
					f.write(CSVSEP.join(labels)+"\n")
					
					for row in self.cursor:
						list = []
						for field in row:
							if field == None:
								field = ''
							else:
								field = str(field)
							if CSVMASK:
								field = '"'+field.replace('"', r'\"')+'"'
							list.append(field)
						f.write(CSVSEP.join(list)+"\n")
					
					f.close()
		else:
			err(_('No database loaded'))
			
	def addemptyrecord(self, this):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			self.sql('INSERT INTO `'+self.browse_current_table+'` DEFAULT VALUES')
			#self.reloadbrowse()
			total = self.refreshscrolllabel()
			self.browse_to(self.browse_current_table, (math.floor(total/self.browse_current_limit)*50), self.browse_current_limit, self.browse_current_search)
		
	def deleterecord(self, this):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			tuple = self.btv.get_selection().get_selected()
			model = tuple[0]
			iter = tuple[1]
			if iter != None:
				rowid = model.get_value(iter, 0)
				if self.sql('DELETE FROM `'+self.browse_current_table+'` WHERE `_rowid_` = ?', (rowid,)):
					del model[iter]
					self.browse_current_count = self.browse_current_count-1
					self.refreshscrolllabel()
			
			
	def preferences(self, this):
		global config, cfgfile, cfgfilename, CSVSEP, CSVMASK
		
		dialogTree = gtk.glade.XML(dist.interfacedir+"/preferences.glade")
		dlg = dialogTree.get_widget('PreferencesDialog')
		
		# LANGUAGE
		
		cb = dialogTree.get_widget('LanguageSelect')
		dialogTree.get_widget('EncodingSelect').set_active(0)
		
		cb = gtk.combo_box_new_text()
		cb.set_size_request(300,30)
		i = 0
		active = 0
		for l in dist.languages:
			cb.append_text(l)
			try:
				if l == config.get('locale', 'lang').strip():
					active = i
			except:
				a = 2
			i += 1
		cb.set_active(active)
		cb.show()
		dialogTree.get_widget('LocaleField').put(cb, 110, 5)
		
		# EXPORT
		dialogTree.get_widget('CsvSep').set_text(CSVSEP)
		dialogTree.get_widget('CsvMask').set_active(CSVMASK)
		
		# RUN
		
		run = dlg.run()
		if run == 3:
			try:
				config.set('locale', 'lang', cb.get_active_text())
				config.set('locale', 'encoding', 'utf-8')
				config.set('export', 'csvsep', dialogTree.get_widget('CsvSep').get_text())
				config.set('export', 'csvmask', dialogTree.get_widget('CsvMask').get_active())
				CSVSEP = dialogTree.get_widget('CsvSep').get_text()
				CSVMASK = dialogTree.get_widget('CsvMask').get_active()
				cfgfile = open(cfgfilename, 'w+')
				config.write(cfgfile)
				print "Writing configuration to "+cfgfilename
				loadconfig()
			finally:
				info(_("You have to restart geek'SQLite to apply some changes like the language"))
				dlg.destroy()
		else:
			dlg.destroy()
			
	def initfilter(self, this):
		cbt = self.mainTree.get_widget('TableSelect').get_active_text()
		if cbt != None and len(self.browse_current_labels) > 0:
			dialogTree = gtk.glade.XML(dist.interfacedir+"/filterdialog.glade")
			dlg = dialogTree.get_widget('FilterDialog')
			
			cb = gtk.combo_box_new_text()
			cb.set_size_request(300,30)
			
			lookforrow = None
			if self.browse_current_search_field and self.browse_current_search_method and self.browse_current_search_filter:
				dialogTree.get_widget('MethodSelect').set_active(self.browse_current_search_method_a)
				dialogTree.get_widget('FilterInput').set_text(self.browse_current_search_filter)
				lookforrow = self.browse_current_search_field
				
			i = 0
			for row in self.browse_current_labels:
				cb.append_text(row)
				if lookforrow == row:
					cb.set_active(i)
				i+=1
		
			cb.show()
			dialogTree.get_widget('FilterField').put(cb, 5, 5)
			run = dlg.run()
			if run == 3:
				cbm = dialogTree.get_widget('MethodSelect')
				fi = dialogTree.get_widget('FilterInput')
				if cb.get_active_text() and cbm.get_active_text(): 
					field = cb.get_active_text()
					method = cbm.get_active_text()
					if method != 'NOTNULL' and method != 'ISNULL':
						filter = " '"+fi.get_text()+"'"
					else:
						filter = ''
					self.browse_to(table=self.browse_current_table,
					start=self.browse_current_start,
					limit=self.browse_current_limit,
					search=field+' '+method+filter)
					self.browse_current_search_field = field
					self.browse_current_search_method = method
					self.browse_current_search_method_a = cbm.get_active()
					self.browse_current_search_filter = fi.get_text()
				else:
					a = 0 # do nothing!
				dlg.destroy()
			else:
				dlg.destroy()
				return None
				
	def newfile(self, this):
		if self.fileopened:
			self.close()
		
		d = filedialog.FileDialog()
		self.filename = d.get_filename(action='save')
		self.do_open()
			
	#### GTK INITIALISATION
	def grab_widgets(self):
		# Main Window
		self.window = self.mainTree.get_widget("MainWindow")
		
	def connect_events(self):
		# Main Window
		dic = {
				"on_MainWindow_destroy" : self.exit,
				"on_MainMenuExit_activate" : self.exit,
				"on_MainMenuAbout_activate" : self.display_about,
				"on_MainMenuOpen_activate" : self.open,
				"on_MainMenuNew_activate" : self.newfile,
				"on_MainMenuClose_activate" : self.close,
				"on_MainMenuTableCreate_activate" : self.table_create,
				"on_MainMenuIndexCreate_activate" : self.index_create,
				"on_MainMenuIndexDelete_activate" : self.index_delete,
				"on_MainMenuTableDelete_activate" : self.table_delete,
				"on_MainMenuTableModify_activate" : self.table_modify,
				"on_MainMenuDropView_activate": self.view_delete,
				"on_MainMenuCreateView_activate": self.view_create,
				"on_MainMenuConfig_activate" : self.preferences,
				"on_ExecButton_activate" : self.execute,
				"on_ExecButton_clicked" : self.execute,
				"on_TableSelect_changed" : self.browse,
				"on_ImportSQL_activate" : self.importSQL,
				"on_ExportSQL_activate" : self.exportSQL,
				"on_ExportCSV_activate" : self.exportCSV,
				"on_ScrollRight_activate" : self.browse_nextpage,
				"on_ScrollRight_clicked" : self.browse_nextpage,
				"on_ScrollLeft_activate" : self.browse_previouspage,
				"on_ScrollLeft_clicked" : self.browse_previouspage,
				"on_ReloadButton_activate" : self.reloadbrowse,
				"on_ReloadButton_clicked" : self.reloadbrowse,
				"on_AddButton_activate" : self.addemptyrecord,
				"on_AddButton_clicked" : self.addemptyrecord,
				"on_DeleteButton_activate" : self.deleterecord,
				"on_DeleteButton_clicked" : self.deleterecord,
				"on_SearchButton_activate" : self.initfilter,
				"on_SearchButton_clicked" : self.initfilter,
			  }
		self.mainTree.signal_autoconnect(dic)
	
	def design_treeviews(self):
		# Structure Treeview
		tv = self.mainTree.get_widget('StructTv')
		
		self.structtv_col = gtk.TreeViewColumn(_('Name'))
		self.structtv_cell = gtk.CellRendererText()
		self.structtv_col.pack_start(self.structtv_cell)
		self.structtv_col.add_attribute(self.structtv_cell, 'text', 0)
		self.structtv_col.set_resizable(True)
		tv.append_column(self.structtv_col)	
		
		self.structtv_col2 = gtk.TreeViewColumn(_('Type'))
		self.structtv_cell2 = gtk.CellRendererText()
		self.structtv_col2.pack_start(self.structtv_cell2)
		self.structtv_col2.add_attribute(self.structtv_cell2, 'text', 1)
		self.structtv_col2.set_resizable(True)
		tv.append_column(self.structtv_col2)	
		
		self.structtv_col3 = gtk.TreeViewColumn(_('Schema'))
		self.structtv_cell3 = gtk.CellRendererText()
		self.structtv_col3.pack_start(self.structtv_cell3)
		self.structtv_col3.add_attribute(self.structtv_cell3, 'text', 2)
		self.structtv_col3.set_resizable(True)
		tv.append_column(self.structtv_col3)	
		
		# Select Table combobox
		combobox = self.mainTree.get_widget('TableSelect')
		cell4 = gtk.CellRendererText()
		combobox.pack_start(cell4, True)
		combobox.add_attribute(cell4, 'text', 0)
		
	def __init__(self):
		# Main Window
		self.mainTree = gtk.glade.XML(dist.interfacedir+"/mainwindow.glade")
		self.grab_widgets()
		self.connect_events()	
		self.design_treeviews()
		self.fileopened = False
		self.browse_current_table = None
		self.browse_current_search_field = None
		self.browse_current_search_method = None
		self.browse_current_search_filter = None
		self.browse_current_labels = []
		self.window.set_icon(gtk.gdk.pixbuf_new_from_file(dist.icon))
		
		if len(sys.argv) == 2:
			self.do_open(sys.argv[1])
		
if __name__ == "__main__":
	
	parser = OptionParser(usage="Usage: %prog [options] [file]", prog="geeksqlite")
	parser.add_option("-c", "--config", dest="cfg", default=None,
					  help="reads configuration from FILE", metavar="FILE")
	parser.add_option("-q", "--quiet",
					  action="store_true", dest="quiet", default=False,
					  help="don't print anything(!) stdout or stderr")
	parser.add_option("-v", "--version",
					  action="store_true", dest="displayversion", default=False,
					  help="displays version information and quits")
	parser.add_option("-l", "--license",
					  action="store_true", dest="displaylicense", default=False,
					  help="displays geek'SQLite's license information and quits")
				
	(options, args) = parser.parse_args()
	
	if options.displayversion:
		print ver_name, ver_version
		print ver_copyright
		sys.exit(0)
	if options.displaylicense:
		print ver_license
		sys.exit(0)
	if options.quiet:
		null = open('/dev/null', 'w')
		sys.stderr = null
		sys.stdout = null
	
	if options.cfg:
		loadconfigfile(options.cfg)
	else:
		loadconfig()
	
	gsl = geeksqliteMain()
	try:
		gtk.main()
	except KeyboardInterrupt:
		try:
			gsl.exit()
		finally:
			sys.exit(0)

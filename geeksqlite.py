#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import filedialog, sys, os, dist

# gettext
gettext.bindtextdomain('geeksqlite', dist.langdir)
gettext.textdomain('geeksqlite')
_ = gettext.gettext
	
def err(text):
	error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR
				, message_format=text
				, buttons=gtk.BUTTONS_OK)
	error_dlg.run()
	error_dlg.destroy()
	
class geeksqliteMain:
	
	def gettablename(self, title):
		dialogTree = gtk.glade.XML(dist.interfacedir+"/tablenamedialog.glade")
		dlg = dialogTree.get_widget('TableNameDialog')
		dlg.set_title(title)
		
		cb = gtk.combo_box_new_text()
		cb.set_size_request(240,30)
		
		result = self.sql('select name, sql from sqlite_master WHERE type = "table";')
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
		
	def browse_to(self, table, start=0, limit=50, search=None):
		self.browse_current_table = table
		self.browse_current_start = start
		self.browse_current_limit = limit
		self.browse_current_search = search
		
		if self.fileopened:
			ef = self.mainTree.get_widget('DataField')
			try:
				ef.remove(self.btv)
				self.btv = False
			except:
				self.btv = False
			try:
				query = "SELECT rowid, * FROM "+table;
				if search != None:
					query += " "+search
				query += " LIMIT "+str(start)+","+str(limit)+";"
				result = self.sql(query)
				ls = False
				C = 0
				any = False
				for row in self.cursor:
					any = True
					l = len(row)
					list = []
					for field in row:
						list.append(str(field))
					if not ls:
						columns = [str] * l
						ls = gtk.ListStore(*columns)
					ls.append(list)
					C += 1
				if any:
					cols = [""]*l
					cells = [""]*l
					labels = [""]*l
					j = 0
					for k in self.cursor.description:
						labels[j] = str(k[0])
						j += 1
					self.btv = gtk.TreeView(ls)
					
					for i in range(0,l):
						cols[i] = gtk.TreeViewColumn(labels[i])
						cells[i] = gtk.CellRendererText()
						cols[i].pack_start(cells[i])
						cols[i].add_attribute(cells[i], 'text', i)
						cols[i].set_resizable(True)
						self.btv.append_column(cols[i])
						self.btv.show()
					ef.add(self.btv)
					scrolllabel = self.mainTree.get_widget('ScrollLabel')
					result2 = self.sql("SELECT * FROM "+table+";")
					total = len(self.cursor.fetchall())
					if total < start+limit:
						self.mainTree.get_widget('ScrollRight').hide()
					else:
						self.mainTree.get_widget('ScrollRight').show()
					if start == 0:
						self.mainTree.get_widget('ScrollLeft').hide()
					else:
						self.mainTree.get_widget('ScrollLeft').show()
					scrolllabel.set_text(str(start+1)+' to '+str(start+C)+' of '+str(total))
			except sqlite3.Error, e:
				ebuf.set_text('[SQLite Error] '+e.args[0])
		
	def do_open(self, file=None):
		if file != None:
			self.filename = file
		if self.filename:
			try:
				self.close()
				self.connection = sqlite3.connect(self.filename)
				self.cursor = self.connection.cursor()
				self.fileopened = True
				self.cursor.execute('select name, sql from sqlite_master WHERE type = "table";')
				self.log_add('-- -- OPEN FILE -- --')
			except:
				err(_('Unable to open database file'))
				self.fileopened = False
		self.reloadstructure()
		self.reloadbrowse()
				
	def log_add(self, text):
		buf = self.mainTree.get_widget('LogMemo').get_buffer()
		buf.insert(buf.get_end_iter(), text+"\n")
		
	def sql(self, text):
		self.log_add(text)
		return self.cursor.execute(text)
		
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
		result = self.sql('select name, sql from sqlite_master WHERE type = "table";')
		for row in self.cursor:
			n = row[0]
			ls.append([n, 'table', row[1]])
			ls2.append([n])
		result = self.sql('select name, sql from sqlite_master WHERE type = "index";')
		for row in self.cursor:
			n = row[0]
			ls.append([n, 'index', row[1]])
		self.mainTree.get_widget('StructTv').set_model(ls)
		self.mainTree.get_widget('TableSelect').set_model(ls2)
		
	#### EVENT HANDLERS
	def close(self, this = None):
		if self.fileopened:
			ls = gtk.ListStore(str, str, str)
			ls2 = gtk.ListStore(str)
			self.mainTree.get_widget('StructTv').set_model(ls)
			self.mainTree.get_widget('TableSelect').set_model(ls2)
			self.connection.commit()
			self.connection.close()
			self.cursor = None
			self.fileopened = False
			self.log_add('-- -- CLOSE FILE -- --')
		else:
			self.fileopened = False
		
	def open(self, this):
		d = filedialog.FileDialog()
		self.filename = d.get_filename(action='open')
		self.do_open()
		
	def table_create(self, this):
		pass
		
	def table_delete(self, this):
		tblname = self.gettablename(_('Drop Table'))
		if tblname:
			self.sql('DROP TABLE '+tblname)
			if tblname == self.browse_current_table:
				self.browse_to('sqlite_master',
				start=0,
				limit=0,
				search=None)
			self.reloadstructure()
		
	def exit(self, this):
		self.close()
		gtk.main_quit(self, this)
		
	def display_about(self, this): # About
		import version as ver
		dialog = gtk.AboutDialog()
		dialog.set_name(ver.name)
		dialog.set_program_name(ver.name)
		dialog.set_version(ver.version)
		dialog.set_copyright(ver.copyright)
		dialog.set_comments(ver.comments)
		dialog.set_license(ver.license)
		dialog.set_website(ver.website)
		dialog.set_website_label(ver.website_label)
		dialog.set_authors(ver.authors)
		dialog.set_documenters(ver.documenters)
		dialog.set_artists(ver.artists)
		dialog.set_translator_credits(ver.translators)
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
					result = self.sql(inpu)
					if inpu.lstrip().upper().startswith("SELECT"):
						ls = False
						for row in self.cursor:
							l = len(row)
							list = []
							for field in row:
								list.append(str(field))
							if not ls:
								columns = [str] * l
								ls = gtk.ListStore(*columns)
							ls.append(list)
						cols = [""]*l
						cells = [""]*l
						labels = [""]*l
						j = 0
						for k in self.cursor.description:
							labels[j] = str(k[0])
							j += 1
						self.exectv = gtk.TreeView(ls)
						for i in range(0,l):
							cols[i] = gtk.TreeViewColumn('')
							cells[i] = gtk.CellRendererText()
							cols[i].pack_start(cells[i])
							cols[i].add_attribute(cells[i], 'text', i)
							cols[i].set_resizable(True)
							self.exectv.append_column(cols[i])
							self.exectv.show()
						ef.add(self.exectv)
					self.reloadstructure()
					self.reloadbrowse()
				except sqlite3.Error, e:
					ebuf.set_text('[SQLite Error] '+e.args[0])
			else:
				ebuf.set_text('[geekSQLite Error] Not a complete statement!')
		else:
			err('No database loaded')
		
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
			err('No database loaded')
	
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
			err('No database loaded')
			
	def addemptyrecord(self, this):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			self.sql('INSERT INTO '+self.browse_current_table+' DEFAULT VALUES')
			self.reloadbrowse()
		
	def deleterecord(self, this):
		cb = self.mainTree.get_widget('TableSelect').get_active_text()
		if cb != None:
			tuple = self.btv.get_selection().get_selected()
			model = tuple[0]
			iter = tuple[1]
			if iter != None:
				rowid = model.get_value(iter, 0)
				self.sql('DELETE FROM '+self.browse_current_table+' WHERE rowid = '+rowid)
			self.reloadbrowse()
			
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
				"on_MainMenuClose_activate" : self.close,
				"on_MainMenuTableCreate_activate" : self.table_create,
				"on_MainMenuTableDelete_activate" : self.table_delete,
				"on_ExecButton_activate" : self.execute,
				"on_ExecButton_clicked" : self.execute,
				"on_TableSelect_changed" : self.browse,
				"on_ImportSQL_activate" : self.importSQL,
				"on_ExportSQL_activate" : self.exportSQL,
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
			  }
		self.mainTree.signal_autoconnect(dic)
	
	def design_treeviews(self):
		# Structure Treeview
		tv = self.mainTree.get_widget('StructTv')
		
		self.structtv_col = gtk.TreeViewColumn('Name')
		self.structtv_cell = gtk.CellRendererText()
		self.structtv_col.pack_start(self.structtv_cell)
		self.structtv_col.add_attribute(self.structtv_cell, 'text', 0)
		self.structtv_col.set_resizable(True)
		tv.append_column(self.structtv_col)	
		
		self.structtv_col2 = gtk.TreeViewColumn('Type')
		self.structtv_cell2 = gtk.CellRendererText()
		self.structtv_col2.pack_start(self.structtv_cell2)
		self.structtv_col2.add_attribute(self.structtv_cell2, 'text', 1)
		self.structtv_col2.set_resizable(True)
		tv.append_column(self.structtv_col2)	
		
		self.structtv_col3 = gtk.TreeViewColumn('Schema')
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
		
		if len(sys.argv) == 2:
			if sys.argv[1] in ('-h', '--help'):
				print """geekSQLite - free Python GTK+ SQLite3 database file browser
USAGE:
geeksqlite [argument]

POSSIBLE ARGUMENTS:
* any sqlite database file (example: geeksqlite test.sqlite)
* -v for version informations
* -l for the license
* -h for this text"""
				sys.exit(0)
			elif sys.argv[1] in ('-v', '--version'):
				import version as ver
				print ver.name, ver.version
				print ver.copyright
				sys.exit(0)
			elif sys.argv[1] in ('-l', '--license'):
				import version as ver
				print ver.license
				sys.exit(0)
			self.do_open(sys.argv[1])
		
if __name__ == "__main__":
	gsl = geeksqliteMain()
	gtk.main()

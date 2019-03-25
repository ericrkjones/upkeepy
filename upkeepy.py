#!/usr/bin/python3
import json
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os

def loadJSONData(file):
	with open(file, 'r') as jsondata:
		d = json.load(jsondata)
	return d


class CardBinStore(Gtk.TreeStore):
	def __init__(self, dirbins):
		'''dirbins is a list of tuples with the structure (top level bin name, directory)'''
		Gtk.TreeStore.__init__(self, str)
		self.dirDict = {}
		for name, directory in dirbins:
			self.dirDict[name] = self.dirTree(directory)
		self.dirTreeStore(self.dirDict, None)

	def dirTree(self, directory):
		output = {}
		for child in sorted(os.listdir(directory)):
			if os.path.isdir(directory+os.sep+child):
				tag = child
				data = self.dirTree(directory+os.sep+child)
			else:
				tag = os.path.splitext(child)[0]
				data = directory+os.sep+child
			output[tag] = data
		return output
				
	def dirTreeStore(self, dictionary, parent):
		for key in dictionary:
			thisrow = self.append(parent, [key])
			if isinstance(dictionary[key], dict):
				self.dirTreeStore(dictionary[key], thisrow)


class MainWindow(Gtk.Window):
	'''Main window class, which contains the listbox showing elements from the database, menu, and preview panes.  '''
	def __init__(self):
		Gtk.Window.__init__(self, title="Upkeepy")
		self.set_default_size(800,600)
		self.resizable = True
		self.menubar = self.buildMenuBar()
		self.sources = self.buildCardSources()
		self.documentpanes = self.buildDocumentPanes()
		self.toppanes = self.buildWindowPanes()
		self.statusbar = Gtk.Statusbar()
		self.mainbox = Gtk.VBox()
		self.mainbox.pack_start(self.menubar, False, False, 0)
		self.mainbox.add(self.toppanes)
		self.mainbox.pack_end(self.statusbar, False, False, 0)
		self.connect("destroy", Gtk.main_quit)
		self.add(self.mainbox)
		
		# Configuration
		self.loadConfiguration()
		

	def loadConfiguration(self):
		self.contextconfig = loadJSONData(os.path.expanduser('~/.local/share/upkeepy/mtg_scryfall-context.json'))
		self.loadSources(os.path.expanduser(self.contextconfig['sourcedir']))
		# self.loadDecks(os.path.expanduser(self.contextconfig['deckdir']))

	def loadSources(self, directory):
		self.sourcestore = CardBinStore((('Sources', os.path.expanduser(self.contextconfig['sourcedir'])), ('Decks', os.path.expanduser(self.contextconfig['deckdir']))))
		self.sourcesview.set_model(self.sourcestore)

	def loadDecks(self, directory):
		self.deckstore = CardBinStore(directory, )
		self.decksview.set_model(self.deckstore)

	def buildMenuBar(self):
		'''Menu bar build routine, to cut down on variables, is handled here'''
		# File menu
		## File menu submenu items and bindings
		submenu_file_new = Gtk.MenuItem("New deck")
		submenu_file_save = Gtk.MenuItem("Save")
		submenu_file_saveas = Gtk.MenuItem("Save as")
		submenu_file_import = Gtk.MenuItem("Import from file")
		submenu_file_export = Gtk.MenuItem("Export to file")
		submenu_file_quit = Gtk.MenuItem("Quit")
		file_quit = submenu_file_quit.connect("activate", Gtk.main_quit)
		
		## Ordered packing of file menu items
		submenu_file = Gtk.Menu()
		submenu_file.append(submenu_file_new)
		submenu_file.append(submenu_file_save)
		submenu_file.append(submenu_file_saveas)
		submenu_file.append(Gtk.SeparatorMenuItem())
		submenu_file.append(submenu_file_import)
		submenu_file.append(submenu_file_export)
		submenu_file.append(Gtk.SeparatorMenuItem())
		submenu_file.append(submenu_file_quit)

		## Top-level file menu
		menu_file = Gtk.MenuItem("File")
		menu_file.set_submenu(submenu_file)
		
		# Edit menu
		## Edit menu submenu items and bindings
		submenu_edit = Gtk.Menu()

		## Ordered packing of file menu items

		## Top-level edit menu
		menu_edit = Gtk.MenuItem("Edit")
		menu_edit.set_submenu(submenu_edit)
		
		# View menu
		## View menu submenu items and bindings

		## Ordered packing of view menu items
		submenu_view = Gtk.Menu()

		## Top-level view menu
		menu_view = Gtk.MenuItem("View")
		menu_view.set_submenu(submenu_view)
		
		# Tools menu
		## Tools menu submenu items and bindings

		## Ordered packing of tools menu items
		submenu_tools = Gtk.Menu()

		## Top-level tools menu
		menu_tools = Gtk.MenuItem("Tools")
		menu_tools.set_submenu(submenu_tools)

		# Help menu
		## Help menu submenu items and bindings

		## Ordered packing of help menu items
		submenu_help = Gtk.Menu()

		## Top-level help menu
		menu_help = Gtk.MenuItem("Help")
		menu_help.set_submenu(submenu_help)

		menubar = Gtk.MenuBar()
		menubar.append(menu_file)
		menubar.append(menu_edit)
		menubar.append(menu_view)
		menubar.append(menu_tools)
		menubar.append(menu_help)

		return menubar
				
	def buildCardSources(self):
		sources_maincolumn = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0)

		sources_scroll = Gtk.ScrolledWindow()
		self.sourcesview = Gtk.TreeView()
		self.sourcesview.set_headers_visible(False)
		self.sourcesview.append_column(sources_maincolumn)
		sources_scroll.add(self.sourcesview)

		# decks_scroll = Gtk.ScrolledWindow()
		# self.decksview = Gtk.TreeView()
		# self.decksview.append_column(decks_maincolumn)
		# decks_scroll.add(self.decksview)

		# Changed to a single treeview
		# cardset_bins = Gtk.VPaned()
		# cardset_bins.add(sources_scroll)
		# cardset_bins.add(decks_scroll)
		# return cardset_bins
		return sources_scroll

	def buildDocumentPanes(self):
		documentpanes_document = Gtk.Frame()
		document = Gtk.TreeView()
		documentpanes_document.add(document)		
		documentpanes_details = Gtk.Frame()
		details = Gtk.VBox()
		details_label = Gtk.Label()
		details_label.set_text("Card Details")
		details_scroll = Gtk.ScrolledWindow()
		details_content = Gtk.ListBox()
		details_scroll.add(details_content)
		details.pack_start(details_label, False, False, 0)
		details.add(details_scroll)
		documentpanes_details.add(details)

		documentpanes = Gtk.HPaned()
		documentpanes.add(documentpanes_document)
		documentpanes.add(documentpanes_details)
		documentpanes.set_wide_handle(True)
		documentpanes.set_position(300)
		#documentpanes.set_border_width(0)

		return documentpanes

	def buildWindowPanes(self):
		toppanes_left = Gtk.Frame()
		toppanes_left.add(self.sources)

		toppanes_right = Gtk.Frame()
		toppanes_right.add(self.documentpanes)
		toppanes = Gtk.HPaned()
		toppanes.add(toppanes_left)
		toppanes.add(toppanes_right)
		toppanes.set_wide_handle(True)
		toppanes.set_position(200)
		#toppanes.set_border_width(0)

		return toppanes

window = MainWindow()
window.show_all()
Gtk.main()

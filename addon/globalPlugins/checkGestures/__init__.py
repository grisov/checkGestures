# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
import globalPluginHandler
from globalVars import appArgs
import gui
import wx
import config
from typing import Callable
from logHandler import log
from scriptHandler import script
from inputCore import InputGesture
from . import base
from .graphui import UnsignedGesturesDialog

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]

curAddon = addonHandler.getCodeAddon()
ADDON_NAME: str = curAddon.manifest['name']
ADDON_SUMMARY: str = curAddon.manifest['summary']


class Duplicates(base.Duplicates):
	# Translators: The title of the gestures list dialog and menu item
	name: str = _("Search for &duplicate gestures")


class Unsigned(base.Unsigned):
	# Translators: The title of the gestures list dialog and menu item
	name: str = _("Gestures &without description")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory: str = ADDON_SUMMARY

	def __init__(self, *args, **kwargs) -> None:
		"""Initialization of the add-on global plugin."""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if appArgs.secure or config.isAppX:
			return
		self.createMenu()

	def createMenu(self) -> None:
		"""Build a submenu in the NVDA "tools" menu."""
		self.menu: wx.Menu = gui.mainFrame.sysTrayIcon.toolsMenu
		subMenu = wx.Menu()
		self.mainItem: wx.MenuItem = self.menu.AppendSubMenu(subMenu, ADDON_SUMMARY)
		checkDuplicatesItem: wx.MenuItem = subMenu.Append(wx.ID_ANY, Duplicates().menuItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckDuplicates, checkDuplicatesItem)
		checkUnsignedItem: wx.MenuItem = subMenu.Append(wx.ID_ANY, Unsigned().menuItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckUnsigned, checkUnsignedItem)
		# Translators: the name of a submenu item
		helpItem: wx.MenuItem = subMenu.Append(wx.ID_ANY, _("&Help"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onHelp, helpItem)

	def terminate(self, *args, **kwargs) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			self.menu.Remove(self.mainItem)
		except (RuntimeError, AttributeError):
			pass

	def checkGestures(self, gestures: base.FilteredGestures) -> None:
		"""Show a list of gestures in a separate window,
		if the gesture collection is empty, a warning is displayed.
		@param gestures: filtered collection of input gestures
		@type gestures: base.FilteredGestures
		"""
		if len(gestures) > 0:
			GesturesDialog = UnsignedGesturesDialog if isinstance(gestures, Duplicates) else UnsignedGesturesDialog
			gui.mainFrame._popupSettingsDialog(GesturesDialog, title=gestures.title, gestures=gestures)
		else:
			gui.messageBox(
				# Translators: Notification of no search results
				message=_("Target gestures not found"),
				caption=gestures.title,
				style=wx.OK | wx.ICON_ERROR,
				parent=gui.mainFrame)

	def onCheckDuplicates(self, event: wx.PyEvent) -> None:
		"""Show the collection of duplicate gestures in separate window.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx.PyEvent
		"""
		self.checkGestures(Duplicates())

	def onCheckUnsigned(self, event: wx.PyEvent) -> None:
		"""Show the collection of gestures wich binded to features without description in separate window.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx.PyEvent
		"""
		self.checkGestures(Unsigned())

	def onHelp(self, event: wx.PyEvent) -> None:
		"""Open the add-on help page in the default browser.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx.PyEvent
		"""
		import webbrowser
		webbrowser.open(curAddon.getDocFilePath())

	@script(description=Duplicates().title)
	def script_duplicates(self, gesture: InputGesture) -> None:
		"""Check the NVDA configuration and display all detected duplicated input gestures.
		@param gesture: the input gesture in question
		@type gesture: InputGesture
		"""
		wx.CallAfter(self.onCheckDuplicates, None)

	@script(description=Unsigned().title)
	def script_unsigned(self, gesture: InputGesture) -> None:
		"""Check the NVDA configuration and display all detected unsigned input gestures.
		@param gesture: the input gesture in question
		@type gesture: InputGesture
		"""
		wx.CallAfter(self.onCheckUnsigned, None)

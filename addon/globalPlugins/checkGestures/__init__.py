#-*- coding:utf-8 -*-
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

from __future__ import annotations
import addonHandler
from logHandler import log
try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to initialise translations. This may be because the addon is running from NVDA scratchpad.")

import os
addonDir = os.path.join(os.path.dirname(__file__), "..", "..")
if isinstance(addonDir, bytes):
	addonDir = addonDir.decode("mbcs")
curAddon = addonHandler.Addon(addonDir)
addonName, addonSummary = curAddon.manifest['name'], curAddon.manifest['summary']

import globalPluginHandler
from globalVars import appArgs
import gui, wx
import config
from scriptHandler import script
from . import base
from .graphui import GesturesListDialog


class Duplicates(base.Duplicates):
	# Translators: The title of the gestures list dialog and menu item
	name: str = _("Search for &duplicate gestures")


class Unsigned(base.Unsigned):
	# Translators: The title of the gestures list dialog and menu item
	name: str = _("Gestures &without description")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory: str = addonSummary

	def __init__(self, *args, **kwargs) -> None:
		"""Initialization of the add-on global plugin."""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if appArgs.secure or config.isAppX:
			return
		self.createMenu()

	def createMenu(self) -> None:
		"""Build a submenu in the NVDA "tools" menu."""
		self.menu = gui.mainFrame.sysTrayIcon.toolsMenu
		subMenu = wx.Menu()
		self.mainItem = self.menu.AppendSubMenu(subMenu, addonSummary)
		checkDuplicatesItem = subMenu.Append(wx.ID_ANY, Duplicates().menuItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckDuplicates, checkDuplicatesItem)
		checkUnsignedItem = subMenu.Append(wx.ID_ANY, Unsigned().menuItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckUnsigned, checkUnsignedItem)
		# Translators: the name of a submenu item
		helpItem = subMenu.Append(wx.ID_ANY, _("&Help"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onHelp, helpItem)

	def terminate(self, *args, **kwargs) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			self.menu.Remove(self.mainItem)
		except (RuntimeError, AttributeError):
			pass

	def checkGestures(self, gestures: base.Gestures) -> None:
		"""Show a list of gestures in a separate window,
		if the gesture collection is empty, a warning is displayed.
		@param gestures: collection of input gestures
		@type gestures: .base.Gestures
		"""
		if len(gestures)>0:
			gui.runScriptModalDialog(GesturesListDialog(parent=gui.mainFrame, title=gestures.title, gestures=gestures))
		else:
			# Translators: Notification of no search results
			gui.messageBox(_("Target gestures not found"),
				caption=gestures.title,
				parent=gui.mainFrame)

	def onCheckDuplicates(self, event: wx._core.PyEvent) -> None:
		"""Show the collection of duplicate gestures in separate window.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx._core.PyEvent
		"""
		event.Skip()
		self.checkGestures(Duplicates())

	def onCheckUnsigned(self, event: wx._core.PyEvent) -> None:
		"""Show the collection of gestures wich binded to features without description in separate window.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx._core.PyEvent
		"""
		event.Skip()
		self.checkGestures(Unsigned())

	def onHelp(self, event: wx._core.PyEvent) -> None:
		"""Open the add-on help page in the default browser.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx._core.PyEvent
		"""
		import webbrowser
		webbrowser.open(curAddon.getDocFilePath())

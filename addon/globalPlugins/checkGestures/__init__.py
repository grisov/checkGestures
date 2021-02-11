#-*- coding:utf-8 -*-
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

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
from .base import Duplicates, Unsigned
from .graphui import GesturesListDialog


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory = addonSummary

	def __init__(self, *args, **kwargs):
		"""Initialization of the add-on."""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if appArgs.secure or config.isAppX:
			return
		self.addMenu()

	def addMenu(self) -> None:
		"""Build a submenu in the "tools" menu."""
		self.menu = gui.mainFrame.sysTrayIcon.toolsMenu
		subMenu = wx.Menu()
		self.mainItem = self.menu.AppendSubMenu(subMenu, addonSummary)
		checkDuplicatesItem = subMenu.Append(wx.ID_ANY, Duplicates().menuItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckDuplicates, checkDuplicatesItem)
		checkUnsignedItem = subMenu.Append(wx.ID_ANY, Unsigned().menuItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckUnsigned, checkUnsignedItem)

	def terminate(self, *args, **kwargs):
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			self.menu.Remove(self.mainItem)
		except (RuntimeError, AttributeError):
			pass

	def checkGestures(self, gestures):
		if len(gestures)>0:
			wx.CallAfter(GesturesListDialog.showDialog, title=gestures.title, gestures=gestures)
		else:
			# Translators: Notification of no search results
			gui.messageBox(_("Target gestures not found"),
				caption=gestures.title,
				parent=gui.mainFrame)

	def onCheckDuplicates(self, event) -> None:
		event.Skip()
		self.checkGestures(Duplicates())

	def onCheckUnsigned(self, event) -> None:
		event.Skip()
		self.checkGestures(Unsigned())

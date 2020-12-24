#-*- coding:utf-8 -*-
# A part of the NVDA Check Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

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
from .base import Gestures


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory = addonSummary

	def __init__(self, *args, **kwargs):
		"""Initialization of the add-on."""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if appArgs.secure or config.isAppX:
			return
		self.addMenuItem()

	def addMenuItem(self) -> None:
		self.menu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.menuItem = self.menu.Append(wx.ID_ANY, addonSummary)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItem, self.menuItem)

	def terminate(self, *args, **kwargs):
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			self.toolsMenu.Remove(self.menuItem)
		except (RuntimeError, AttributeError):
			pass

	def onMenuItem(self, event) -> None:
		gestures = Gestures()
		gestures.initialize()

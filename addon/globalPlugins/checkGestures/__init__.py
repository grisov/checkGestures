# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

from collections.abc import Callable
from typing import Any, cast, override

import addonHandler
import config
import core
import globalPluginHandler
import gui
import wx
from globalVars import appArgs
from inputCore import InputGesture
from logHandler import log
from scriptHandler import script

from . import base
from .configuration import ADDON_SUMMARY, getKnownDuplicates, isCheckOnStartup, rememberDuplicates
from .graphui import DuplicatedGesturesDialog, UnsignedGesturesDialog

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]

# The manifest of the add-on has no type annotations
_addon = cast(Any, addonHandler).getCodeAddon()
# Delay after NVDA has started before the search for new duplicate gestures, in milliseconds,
# so the add-ons and other components that are loaded after NVDA has started have bound their gestures too
STARTUP_CHECK_DELAY = 5000


class Duplicates(base.Duplicates):
	# Translators: The title of the gestures list dialog and menu item
	name: str = _("Search for &duplicate gestures")


class Unsigned(base.Unsigned):
	# Translators: The title of the gestures list dialog and menu item
	name: str = _("Gestures &without description")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""

	scriptCategory: str = ADDON_SUMMARY

	@override
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""Initialization of the add-on global plugin."""
		super().__init__(*args, **kwargs)
		if appArgs.secure or config.isAppX:
			return
		self.createMenu()
		# core.postNvdaStartup of NVDA has no type annotations
		cast(Any, core).postNvdaStartup.register(self.onNvdaStartup)

	def createMenu(self) -> None:
		"""Build a submenu in the NVDA "tools" menu."""
		# gui.mainFrame is None only until the GUI of NVDA has been initialized, before the plugins are loaded,
		# and wx.EvtHandler.Bind has incomplete type annotations
		sysTrayIcon = cast(Any, gui.mainFrame).sysTrayIcon
		self.menu: wx.Menu = sysTrayIcon.toolsMenu
		subMenu = wx.Menu()
		self.mainItem: wx.MenuItem = self.menu.AppendSubMenu(subMenu, ADDON_SUMMARY)
		checkDuplicatesItem: wx.MenuItem = subMenu.Append(wx.ID_ANY, Duplicates().menuItem)
		sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckDuplicates, checkDuplicatesItem)
		checkUnsignedItem: wx.MenuItem = subMenu.Append(wx.ID_ANY, Unsigned().menuItem)
		sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckUnsigned, checkUnsignedItem)
		# Translators: the name of a submenu item
		helpItem: wx.MenuItem = subMenu.Append(wx.ID_ANY, _("&Help"))
		sysTrayIcon.Bind(wx.EVT_MENU, self.onHelp, helpItem)

	@override
	def terminate(self) -> None:
		"""This will be called when NVDA is finished with this global plugin"""
		try:
			_ = self.menu.Remove(self.mainItem)
		except (RuntimeError, AttributeError):
			pass
		_ = cast(Any, core).postNvdaStartup.unregister(self.onNvdaStartup)
		super().terminate()

	def onNvdaStartup(self) -> None:
		"""Schedule the search for new duplicate gestures, as late as possible after NVDA has started."""
		cast(Any, core).callLater(STARTUP_CHECK_DELAY, self.checkOnStartup)

	def checkOnStartup(self) -> None:
		"""Show the duplicate gestures if new ones have appeared since the last search,
		e.g. after an add-on has been installed, and if it is enabled in the add-on configuration.
		The duplicates are remembered when the window is closed with OK; after Cancel they are shown again next time.
		"""
		if not isCheckOnStartup():
			return
		duplicates = Duplicates()
		signatures = base.getSignatures(duplicates.groups())
		if signatures - getKnownDuplicates():
			self.showGestures(duplicates)
		else:
			# Nothing new: the duplicates that have been resolved meanwhile are forgotten
			rememberDuplicates(signatures)

	def checkGestures(self, gestures: base.FilteredGestures) -> None:
		"""Show a list of gestures in a separate window,
		if the gesture collection is empty, a warning is displayed.
		@param gestures: filtered collection of input gestures
		@type gestures: base.FilteredGestures
		"""
		if len(gestures) > 0:
			self.showGestures(gestures)
		else:
			# The pressed button is not needed; "_" cannot take the result, it translates the message below
			gui.messageBox(  # pyright: ignore[reportUnusedCallResult]
				# Translators: Notification of no search results
				message=_("Target gestures not found"),
				caption=gestures.title,
				style=wx.OK | wx.ICON_ERROR,
				parent=gui.mainFrame,
			)

	def showGestures(self, gestures: base.FilteredGestures) -> None:
		"""Show the collection of gestures in a separate window.
		@param gestures: filtered collection of input gestures
		@type gestures: base.FilteredGestures
		"""
		GesturesDialog = (
			DuplicatedGesturesDialog if isinstance(gestures, Duplicates) else UnsignedGesturesDialog
		)
		# gui.mainFrame is None only until the GUI of NVDA has been initialized
		cast(Any, gui.mainFrame).popupSettingsDialog(
			GesturesDialog,
			title=gestures.title,
			gestures=gestures,
		)

	def onCheckDuplicates(self, event: wx.PyEvent | None) -> None:
		"""Show the collection of duplicate gestures in separate window.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx.PyEvent | None
		"""
		self.checkGestures(Duplicates())

	def onCheckUnsigned(self, event: wx.PyEvent | None) -> None:
		"""Show the collection of gestures wich binded to features without description in separate window.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx.PyEvent | None
		"""
		self.checkGestures(Unsigned())

	def onHelp(self, event: wx.PyEvent | None) -> None:
		"""Open the add-on help page in the default browser.
		@param event: event binder object that specifies the activation of wx.Menu item
		@type event: wx.PyEvent | None
		"""
		import webbrowser

		_ = webbrowser.open(_addon.getDocFilePath())

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

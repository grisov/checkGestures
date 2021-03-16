# graphui.py
# Graphical interface components
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import wx
import gui
from gui.settingsDialogs import SettingsDialog
from gui.nvdaControls import AutoWidthColumnListCtrl
from gui.inputGestures import InputGesturesDialog
from inputCore import getDisplayTextForGestureIdentifier
from typing import Callable
import addonHandler
from logHandler import log
from .base import FilteredGestures

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]


class InputGesturesDialogWithSearch(InputGesturesDialog):
	"""Overridden standard NVDA Input Gestures dialog with search at initialization."""

	def __init__(self, parent: wx.Window, search: str = '', *args, **kwargs) -> None:
		"""Initialization of the Input Gestures dialog with a search query.
		@param parent: The parent for this dialog.
		@type parent: wx.Window
		@param search: Search query.
		@type search: str
		"""
		super(InputGesturesDialogWithSearch, self).__init__(parent, *args, **kwargs)
		search and self.filterCtrl.SetValue(search)


class GesturesListDialog(SettingsDialog):
	"""Dialog window to display a collection of input gestures.
	@ivar title: The title of the dialog.
	@type title: str
	"""

	def __init__(
			self,
			parent: wx.Window,
			title: str,
			gestures: FilteredGestures,
			*args, **kwargs) -> None:
		"""Initialization of the graphical dialog.
		@param parent: The parent window for this dialog
		@type parent: wx.Window
		@param title: the title of the dialog
		@type title: str
		@param gestures: collection of the filtered input gestures
		@type gestures: FilteredGestures
		"""
		self.title = title
		self.gestures = gestures
		super(GesturesListDialog, self).__init__(parent, *args, **kwargs)

	def makeSettings(self, sizer: wx.Sizer) -> None:
		"""Populate the dialog with WX controls.
		@param sizer: The sizer to which to add the WX controls.
		@type sizer: wx.Sizer
		"""
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		self.gesturesList = sHelper.addLabeledControl(
			# Translators: Label above the list of found gestures
			_("Select a gesture from the list"),
			AutoWidthColumnListCtrl,
			autoSizeColumn=1,  # The replacement column is likely to need the most space
			itemTextCallable=None,
			style=wx.LC_REPORT | wx.LC_SINGLE_SEL
		)
		# Translators: The label for a first column in the list of gestures
		self.gesturesList.InsertColumn(0, _("Gesture"), width=150)
		# Translators: The label for the second column in the list of gestures
		self.gesturesList.InsertColumn(1, _("Script description or function name"))
		# Translators: The label for the third column in the list of gestures
		self.gesturesList.InsertColumn(2, _("Category"), width=150)

		sizer.Fit(self)
		self.Center(wx.BOTH | wx.Center)

		# Fill in the list of available input gestures
		gestureDisplayText = lambda gest: "{1} ({0})".format(*getDisplayTextForGestureIdentifier(gest))  # noqa E731 do not assign a lambda expression, use a def
		for gesture in sorted(self.gestures, key=lambda x: x.gesture):
			self.gesturesList.Append((
				gestureDisplayText(gesture.gesture),
				gesture.displayName or gesture.scriptName,
				gesture.category or f"[{gesture.moduleName}]"
			))
		self.gesturesList.SetFocus()
		self.gesturesList.Focus(0)
		self.gesturesList.Select(0)

	def unsignedGestureWarning(self) -> bool:
		"""Display the warning if the selected gesture is not presented in the Input Gestures dialog.
		@return: an indication of whether the selected gesture is not presented in the Input gestures dialog
		@rtype: bool
		"""
		category: str = self.gesturesList.GetItemText(self.gesturesList.GetFocusedItem(), 2)
		isUnsigned: bool = category.startswith('[') and category.endswith(']')
		if isUnsigned:
			gui.messageBox(
				# Translators: Message that reports about the absence of the selected gesture in the Input Gestures dialog
				_("This gesture is not represented in the NVDA Input Gestures dialog."),
				# Translators: The title of the window that reports the lack of description of the selected gesture
				caption=_("Gesture without description"),
				parent=self)
		return isUnsigned

	def _enterActivatesOk_ctrlSActivatesApply(self, event: wx.PyEvent) -> None:
		"""Overridden method that performed when pressing keys.
		@param event: event binder object that handles keystrokes
		@type event: wx.PyEvent
		"""
		if event.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			if self.unsignedGestureWarning():
				return
			self.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK))
		event.Skip()

	def onOk(self, event: wx.PyEvent) -> None:
		"""Overridden method that is executed when the Ok button is activated.
		@param event: event binder object that handles the activation of the OK button
		@type event: wx.PyEvent
		"""
		event.Skip()
		self.Destroy()
		if self.unsignedGestureWarning():
			return
		gui.mainFrame._popupSettingsDialog(
			InputGesturesDialogWithSearch,
			search=self.gesturesList.GetItemText(self.gesturesList.GetFocusedItem(), 1))

	def postInit(self) -> None:
		"""Called after the dialog has been created."""
		self.gesturesList.SetFocus()

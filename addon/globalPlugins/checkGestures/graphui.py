#graphui.py
# Graphical interface components
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

import wx
import gui
from gui.settingsDialogs import SettingsDialog
from gui.nvdaControls import AutoWidthColumnListCtrl
from gui.inputGestures import InputGesturesDialog
from inputCore import getDisplayTextForGestureIdentifier


class InputGesturesDialogWithSearch(InputGesturesDialog):

	def __init__(self, parent, search: str='', *args, **kwargs):
		super(InputGesturesDialogWithSearch, self).__init__(parent, *args, **kwargs)
		search and self.filterCtrl.SetValue(search)


class GesturesListDialog(SettingsDialog):

	def __init__(self, title, gestures, *args, **kwargs):
		self.title = title
		self.gestures = gestures
		super(GesturesListDialog, self).__init__(*args, **kwargs)

	def makeSettings(self, sizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		self.gesturesList = sHelper.addLabeledControl(
			# Translators: Label above the list of found gestures
			_("Select a gesture from the list"),
			AutoWidthColumnListCtrl,
			autoSizeColumn=1, # The replacement column is likely to need the most space
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
		gestureDisplayText = lambda gest: "{1} ({0})".format(*getDisplayTextForGestureIdentifier(gest))
		for gesture in sorted(self.gestures, key=lambda x: x.gesture):
			self.gesturesList.Append((gestureDisplayText(gesture.gesture), gesture.displayName or gesture.scriptName, gesture.category or f"[{gesture.moduleName}]"))
		self.gesturesList.SetFocus()
		self.gesturesList.Focus(0)
		self.gesturesList.Select(0)

	def _enterActivatesOk_ctrlSActivatesApply(self, event) -> None:
		"""Performed when pressing keys.
		@param event: event binder object that handles keystrokes
		@type event: wx.core.PyEventBinder
		"""
		key = event.GetKeyCode()
		super(GesturesListDialog, self)._enterActivatesOk_ctrlSActivatesApply(event)

	def onOk(self, event) -> None:
		"""Activation of the selected online service.
		@param event: event binder object that handles the activation of the button or ListItem element
		@type event: wx.core.PyEventBinder
		"""
		event.Skip()
		category = self.gesturesList.GetItemText(self.gesturesList.GetFocusedItem(), 2)
		if category.startswith('[') and category.endswith(']'):
			# Translators: The message that reports about the absence of the selected gesture in the NVDA Input Gestures dialog
			gui.messageBox(_("This gesture is not represented in the NVDA Input Gestures dialog."),
				# Translators: The title of the window that reports the lack of description of the selected gesture
				caption=_("Gesture without description"),
				parent=self)
		else:
			self.Destroy()
			gui.mainFrame._popupSettingsDialog(InputGesturesDialogWithSearch, search=self.gesturesList.GetItemText(self.gesturesList.GetFocusedItem(), 1))

	def postInit(self):
		self.gesturesList.SetFocus()

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
from gui.nvdaControls import AutoWidthColumnListCtrl
from gui.inputGestures import InputGesturesDialog
from inputCore import getDisplayTextForGestureIdentifier


class InputGesturesDialogWithSearch(InputGesturesDialog):

	def __init__(self, parent, search: str='', *args, **kwargs):
		super(InputGesturesDialogWithSearch, self).__init__(parent, *args, **kwargs)
		search and self.filterCtrl.SetValue(search)


class SingletonDialog(wx.Dialog):
	instance = None

	def __new__(cls, *args, **kwargs):
		if cls.instance is None:
			return super(SingletonDialog, cls).__new__(cls, *args, **kwargs)
		return cls.instance

	def __init__(self, *args, **kwargs):
		if self.__class__.instance is None:
			self.__class__.instance = self
			super(SingletonDialog, self).__init__(parent=gui.mainFrame, id=wx.ID_ANY, *args, **kwargs)

	def onClose(self, event):
		self.__class__.instance = None
		from tones import beep
		beep(3333, 100)
		self.Destroy()

	def __del__(self):
		self.__class__.instance = None

	@classmethod
	def showDialog(cls, *args, **kwargs):
		gui.mainFrame.prePopup()
		dlg = cls(*args, **kwargs)
		dlg and dlg.Show()
		gui.mainFrame.postPopup()


class GesturesListDialog(SingletonDialog):

	def __init__(self, title: str, gestures, *args, **kwargs):
		super(GesturesListDialog, self).__init__(title=title, *args, **kwargs)
		sizer = wx.BoxSizer(wx.VERTICAL)
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

		# Buttons at the bottom of the dialog box
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		self.okButton = wx.Button(self, id=wx.ID_OK)
		buttons.Add(self.okButton)
		cancelButton = wx.Button(self, id=wx.ID_CANCEL)
		buttons.Add(cancelButton)
		sizer.Add(buttons, flag=wx.BOTTOM)
		sizer.Fit(self)
		self.SetSizer(sizer)
		self.Center(wx.BOTH | wx.Center)

		# Fill in the list of available input gestures
		gestureDisplayText = lambda gest: "{1} ({0})".format(*getDisplayTextForGestureIdentifier(gest))
		for gesture in sorted(gestures, key=lambda x: x.gesture):
			self.gesturesList.Append((gestureDisplayText(gesture.gesture), gesture.displayName or gesture.scriptName, gesture.category or f"[{gesture.moduleName}]"))
		self.gesturesList.SetFocus()
		self.gesturesList.Focus(0)
		self.gesturesList.Select(0)

		# Binding dialog box elements to handler methods
		self.gesturesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onActivateItem)
		self.okButton.Bind(wx.EVT_BUTTON, self.onActivateItem)
		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

	def onKeyPress(self, event) -> None:
		"""Performed when pressing keys.
		@param event: event binder object that handles keystrokes
		@type event: wx.core.PyEventBinder
		"""
		key = event.GetKeyCode()
		event.Skip()
		#self.Close()

	def onActivateItem(self, event) -> None:
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
			gui.mainFrame._popupSettingsDialog(InputGesturesDialogWithSearch, search=self.gesturesList.GetItemText(self.gesturesList.GetFocusedItem(), 1))
			self.Close()

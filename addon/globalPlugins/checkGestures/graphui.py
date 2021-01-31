#graphui.py
# Graphical interface components
# A part of the NVDA Check Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import wx
import gui
from gui.nvdaControls import AutoWidthColumnListCtrl


class GesturesListDialog(wx.Dialog):

	def __init__(self, parent, id: int, title: str, gestures, *args, **kwargs):
		super(GesturesListDialog, self).__init__(parent, id, title=title, *args, **kwargs)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		self.gesturesList = sHelper.addLabeledControl(
			# Translators: 
			_("Select a gesture from the list"),
			AutoWidthColumnListCtrl,
			autoSizeColumn=1, # The replacement column is likely to need the most space
			itemTextCallable=None,
			style=wx.LC_REPORT | wx.LC_SINGLE_SEL
		)
		# Translators: The label for a column in the list of gestures
		self.gesturesList.InsertColumn(0, _("Gesture"), width=100)
		# Translators: The label for a column in the list of gestures
		self.gesturesList.InsertColumn(1, _("Function description or script name"))
		# Translators: The label for a column in the list of gestures
		self.gesturesList.InsertColumn(2, _("Category"), width=100)

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

		# Fill in the list of available services
		for gesture in sorted(gestures, key=lambda x: x.gesture):
			self.gesturesList.Append((gesture.gesture, gesture.displayName or gesture.scriptName, gesture.category or gesture.moduleName))
		self.gesturesList.SetFocus()
		self.gesturesList.Focus(0)
		self.gesturesList.Select(0)

		# Binding dialog box elements to handler methods
		self.gesturesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onSelectGesture)
		self.okButton.Bind(wx.EVT_BUTTON, self.onSelectGesture)
		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

	def onKeyPress(self, event) -> None:
		"""Performed when pressing keys.
		@param event: event binder object that handles keystrokes
		@type event: wx.core.PyEventBinder
		"""
		key = event.GetKeyCode()
		event.Skip()
		#self.Close()

	def onSelectGesture(self, event) -> None:
		"""Activation of the selected online service.
		@param event: event binder object that handles the activation of the button or ListItem element
		@type event: wx.core.PyEventBinder
		"""
		event.Skip()
		from tones import beep
		beep(3333, 33)
		#self.Close()

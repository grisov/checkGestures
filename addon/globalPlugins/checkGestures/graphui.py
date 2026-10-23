# graphui.py
# Graphical interface components
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

# wxPython has incomplete type annotations and the GUI helpers of NVDA have none, so the types returned
# by most GUI calls in this file are unknown to the type checker, and many wx methods return values
# that are not needed here (e.g. whether a control has been focused). Only these rules are relaxed for this file.
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
# pyright: reportUnusedCallResult=false

from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import Any, cast, override

import addonHandler
import gui
import wx
from gui.inputGestures import InputGesturesDialog
from gui.nvdaControls import AutoWidthColumnListCtrl
from gui.settingsDialogs import SettingsDialog
from inputCore import getDisplayTextForGestureIdentifier
from logHandler import log

from .base import DuplicateGroup, Duplicates, FilteredGestures, Gesture, getSignatures
from .configuration import isCheckOnStartup, rememberDuplicates, setCheckOnStartup, updateKnownDuplicates

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]


def describeGesture(identifier: str) -> tuple[str, str]:
	"""Get the source and the keys of the input gesture as NVDA shows them, e.g. ("keyboard, all layouts", "NVDA+F1").
	If NVDA cannot describe the gesture, e.g. its source is not registered because its add-on is not running,
	the parts of the identifier are shown as they are, as in the NVDA Input Gestures dialog.
	@param identifier: the identifier of the input gesture
	@type identifier: str
	@return: the source and the keys of the gesture
	@rtype: tuple[str, str]
	"""
	try:
		source, keys = getDisplayTextForGestureIdentifier(identifier)
	except LookupError:
		source, _separator, keys = identifier.partition(":")
	return source, keys


def getGestureDisplayText(identifier: str) -> str:
	"""Get the text of the input gesture as NVDA shows it, with its source, e.g. "NVDA+F1 (keyboard)".
	@param identifier: the identifier of the input gesture
	@type identifier: str
	@return: the text of the gesture
	@rtype: str
	"""
	source, keys = describeGesture(identifier)
	return f"{keys} ({source})"


def getGestureSource(identifier: str) -> str:
	"""Get the source of the input gesture as NVDA shows it, e.g. "keyboard, all layouts".
	@param identifier: the identifier of the input gesture
	@type identifier: str
	@return: the source of the gesture
	@rtype: str
	"""
	return describeGesture(identifier)[0]


def getDuplicateDisplayText(group: DuplicateGroup) -> str:
	"""Get the text of the keys of a duplicate with the sources of its gestures, e.g. "NVDA+F1 (keyboard, all layouts)".
	A duplicate can mix the gestures for all keyboard layouts and for the current one, then both sources are shown.
	@param group: the duplicate
	@type group: DuplicateGroup
	@return: the text of the duplicate
	@rtype: str
	"""
	keys = describeGesture(group.key)[1]
	sources = sorted({getGestureSource(gesture.gesture) for gesture in group.gestures})
	return f"{keys} ({'; '.join(sources)})"


class InputGesturesDialogWithSearch(InputGesturesDialog):
	"""Overridden standard NVDA Input Gestures dialog with search at initialization
	and, if possible, with the given gesture selected.
	"""

	def __init__(
		self,
		parent: wx.Window,
		search: str = "",
		gesture: Gesture | None = None,
		*args: Any,
		**kwargs: Any,
	) -> None:
		"""Initialization of the Input Gestures dialog with a search query.
		@param parent: The parent for this dialog.
		@type parent: wx.Window
		@param search: Search query.
		@type search: str
		@param gesture: the gesture to select after the search
		@type gesture: Gesture | None
		"""
		# SettingsDialog works with any parent window, NVDA annotates it as a dialog
		super().__init__(parent, *args, **kwargs)  # pyright: ignore[reportArgumentType]
		if search:
			self.filterCtrl.SetValue(search)
		if gesture is not None:
			# Selected after the dialog has been shown, so the selected item gets the focus
			wx.CallAfter(self.selectGesture, gesture)

	def selectGesture(self, gesture: Gesture) -> None:
		"""Expand the category and the script of the gesture and select the gesture itself,
		so it can be changed or removed at once. This uses the internal view model of the NVDA dialog,
		which may change in a future version of NVDA: then only the search result is shown, as before.
		@param gesture: the gesture to select
		@type gesture: Gesture
		"""
		try:
			if not self.findAndSelect(gesture):
				log.debugWarning(f"The gesture is not found in the Input Gestures dialog: {gesture!r}")
		except Exception:
			log.debugWarning("Unable to select the gesture in the Input Gestures dialog", exc_info=True)

	def findAndSelect(self, gesture: Gesture) -> bool:
		"""Find the gesture in the internal view model of the NVDA dialog and select it.
		@param gesture: the gesture to select
		@type gesture: Gesture
		@return: whether the script of the gesture has been found and selected
		@rtype: bool
		"""
		# The view model of the NVDA dialog is internal and has no complete type annotations
		dialog = cast(Any, self)
		script = (gesture.scriptName, gesture.moduleName, gesture.className)
		for categoryVM in dialog.gesturesVM.filteredGestures:
			if categoryVM.displayName != gesture.category:
				continue
			for scriptVM in categoryVM.scripts:
				info = scriptVM.scriptInfo
				if (info.scriptName, info.moduleName, info.className) != script:
					continue
				gestureVM = next(
					(
						item
						for item in scriptVM.gestures
						if getattr(item, "normalizedGestureIdentifier", None) == gesture.gesture
					),
					None,
				)
				# Without the gesture, e.g. if it has been removed meanwhile, its script is selected
				dialog.tree.doRefresh(focus=(categoryVM, scriptVM, gestureVM))
				return True
		return False


class BaseGesturesDialog(SettingsDialog, metaclass=ABCMeta):
	"""Base dialog window to display a collection of input gestures.
	@ivar title: The title of the dialog.
	@type title: str
	"""

	def __init__(
		self,
		parent: wx.Window,
		title: str,
		gestures: FilteredGestures,
		*args: Any,
		**kwargs: Any,
	) -> None:
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
		super().__init__(parent, *args, **kwargs)

	@abstractmethod
	def gestureInFocus(self) -> Gesture | None:
		"""The gesture of the item in focus.
		@return: the gesture, None if the item in focus is not a gesture, e.g. a branch of the tree
		@rtype: Gesture | None
		"""
		raise NotImplementedError("This method must be overridden in the child class!")

	def unsignedGestureWarning(self) -> bool:
		"""Display the warning if the selected gesture is not presented in the Input Gestures dialog.
		@return: an indication of whether the selected gesture is not presented in the Input gestures dialog
		@rtype: bool
		"""
		gesture = self.gestureInFocus()
		isUnsigned = gesture is not None and gesture.isUnsigned
		if isUnsigned:
			gui.messageBox(
				# Translators: Message that reports about the absence of the selected gesture in the Input Gestures dialog
				_("This gesture is not represented in the NVDA Input Gestures dialog."),
				# Translators: The title of the window that reports the lack of description of the selected gesture
				caption=_("Gesture without description"),
				style=wx.OK | wx.ICON_ERROR,
				parent=self,
			)
		return isUnsigned

	@override
	def _enterActivatesOk_ctrlSActivatesApply(self, evt: wx.PyEvent) -> None:
		"""Overridden method that performed when pressing keys.
		@param evt: event binder object that handles keystrokes
		@type evt: wx.PyEvent
		"""
		if evt.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			if self.unsignedGestureWarning():
				return
			self.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK))
		evt.Skip()

	@override
	def onOk(self, evt: wx.CommandEvent) -> None:
		"""Overridden method that is executed when the Ok button is activated:
		the gesture in focus is shown in the Input Gestures dialog.
		@param evt: event binder object that handles the activation of the OK button
		@type evt: wx.CommandEvent
		"""
		gesture = self.gestureInFocus()
		if self.unsignedGestureWarning():
			return
		self.onAccepted()
		evt.Skip()
		self.Destroy()
		if gesture is None:
			return
		# gui.mainFrame is None only until the GUI of NVDA has been initialized
		cast(Any, gui.mainFrame).popupSettingsDialog(
			InputGesturesDialogWithSearch,
			search=gesture.displayName or gesture.scriptName,
			gesture=gesture,
		)

	def onAccepted(self) -> None:
		"""Called when the window is closed with OK, before the gesture in focus is shown."""
		pass


class UnsignedGesturesDialog(BaseGesturesDialog):
	"""Dialog window to display a collection of unsigned input gestures."""

	gesturesList: AutoWidthColumnListCtrl

	@override
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
			style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
		)
		# Translators: The label for a first column in the list of gestures
		self.gesturesList.InsertColumn(0, _("Gesture"), width=150)
		# Translators: The label for the second column in the list of gestures
		self.gesturesList.InsertColumn(1, _("Script description or function name"))
		# Translators: The label for the third column in the list of gestures
		self.gesturesList.InsertColumn(2, _("Category"), width=150)

		sizer.Fit(self)
		self.Center(wx.BOTH | wx.Center)

		# Fill in the list of available input gestures, in the order kept for gestureInFocus
		self._listedGestures = sorted(self.gestures, key=lambda x: x.gesture)
		for gesture in self._listedGestures:
			self.gesturesList.Append(
				(
					getGestureDisplayText(gesture.gesture),
					gesture.displayName or gesture.scriptName,
					gesture.categoryLabel,
				),
			)
		self.gesturesList.SetFocus()
		self.gesturesList.Focus(0)
		self.gesturesList.Select(0)

	@override
	def postInit(self) -> None:
		"""Called after the dialog has been created."""
		self.gesturesList.SetFocus()

	@override
	def gestureInFocus(self) -> Gesture | None:
		"""The gesture of the item in focus.
		@return: the gesture, None if no item is in focus
		@rtype: Gesture | None
		"""
		index: int = self.gesturesList.GetFocusedItem()
		return self._listedGestures[index] if 0 <= index < len(self._listedGestures) else None


class DuplicatedGesturesDialog(BaseGesturesDialog):
	"""Dialog window to display the duplicated input gestures as a tree:
	the keys of each duplicate with their keyboard layouts, then the categories, then the scripts.
	"""

	gesturesTree: wx.TreeCtrl

	@override
	def makeSettings(self, sizer: wx.Sizer) -> None:
		"""Populate the dialog with WX controls.
		@param sizer: The sizer to which to add the WX controls.
		@type sizer: wx.Sizer
		"""
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		self.gesturesTree = tree = sHelper.addLabeledControl(
			# Translators: Label in the window displaying duplicate gestures
			_("Select a gesture from the list"),
			wx.TreeCtrl,
			size=wx.Size(600, 400),
			style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE,
		)
		tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated)
		self.noStartupCheck = sHelper.addItem(
			# Translators: A check box in the window of duplicate gestures
			wx.CheckBox(self, label=_("&Don't show this window on startup")),
		)
		self.noStartupCheck.SetValue(not isCheckOnStartup())
		self.noStartupCheck.Bind(wx.EVT_CHECKBOX, self.onNoStartupCheck)

		sizer.Fit(self)
		self.Center(wx.BOTH | wx.Center)

		# Fill in the tree, all branches are collapsed
		root = tree.AddRoot("")
		groups = self.gestures.groups() if isinstance(self.gestures, Duplicates) else []
		# The duplicates shown in the window, remembered when it is closed with OK
		self._groups = groups
		updateKnownDuplicates(getSignatures(groups))
		for group in sorted(groups, key=lambda item: getDuplicateDisplayText(item).casefold()):
			groupItem = tree.AppendItem(root, getDuplicateDisplayText(group))
			# The layout of each script is shown only if the duplicate mixes several layouts
			isMixed = len({getGestureSource(gesture.gesture) for gesture in group.gestures}) > 1
			for category, gestures in group.categories():
				categoryItem = tree.AppendItem(groupItem, category)
				for gesture in gestures:
					label = gesture.displayName or gesture.scriptName
					if isMixed:
						label = f"{label} ({getGestureSource(gesture.gesture)})"
					tree.AppendItem(categoryItem, label, data=gesture)
		first, _cookie = tree.GetFirstChild(root)
		if first.IsOk():
			tree.SelectItem(first)

	@override
	def postInit(self) -> None:
		"""Called after the dialog has been created."""
		self.gesturesTree.SetFocus()

	@override
	def gestureInFocus(self) -> Gesture | None:
		"""The gesture of the item in focus.
		@return: the gesture, None if the item in focus is a branch of the tree
		@rtype: Gesture | None
		"""
		item = self.gesturesTree.GetFocusedItem()
		data = self.gesturesTree.GetItemData(item) if item.IsOk() else None
		return data if isinstance(data, Gesture) else None

	@override
	def _enterActivatesOk_ctrlSActivatesApply(self, evt: wx.PyEvent) -> None:
		"""Enter on a branch of the tree expands or collapses it, Enter on a gesture opens it.
		@param evt: event binder object that handles keystrokes
		@type evt: wx.PyEvent
		"""
		if evt.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and self.gestureInFocus() is None:
			item = self.gesturesTree.GetFocusedItem()
			if item.IsOk():
				self.gesturesTree.Toggle(item)
			return
		super()._enterActivatesOk_ctrlSActivatesApply(evt)

	@override
	def onAccepted(self) -> None:
		"""The duplicates in the window have been seen, so they are not shown again when NVDA starts,
		until new ones appear. After Cancel or Escape they are shown again when NVDA starts next time.
		"""
		rememberDuplicates(getSignatures(self._groups))

	def onNoStartupCheck(self, evt: wx.CommandEvent) -> None:
		"""Save the option at once, so it applies whichever button closes the window.
		@param evt: event binder object that handles the change of the check box
		@type evt: wx.CommandEvent
		"""
		setCheckOnStartup(not self.noStartupCheck.GetValue())

	def onItemActivated(self, evt: wx.TreeEvent) -> None:
		"""A double click on a gesture opens it, a double click on a branch expands or collapses it as usual.
		@param evt: event binder object that handles the activation of an item of the tree
		@type evt: wx.TreeEvent
		"""
		if self.gestureInFocus() is None:
			evt.Skip()
			return
		self.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK))

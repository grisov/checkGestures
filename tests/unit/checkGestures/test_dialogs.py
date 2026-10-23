# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

"""The windows of the add-on built with real wx controls: the tree of duplicates, the list of gestures
without description and the selection of a gesture in the Input Gestures dialog.
"""

import types

import wx

from checkGesturesSupport import addon, events, log, module
from checkGesturesSupport.case import AddonTestCase

graphui = module("graphui")
configuration = module("configuration")


def key(code):
	"""A key press for the key handler of the dialogs."""
	skipped = []
	return types.SimpleNamespace(KeyCode=code, Skip=lambda: skipped.append(True), skipped=skipped)


class TreeTestCase(AddonTestCase):
	def createTree(self):
		self.dialog = self.createDialog(graphui.DuplicatedGesturesDialog, addon.Duplicates())
		return self.dialog.gesturesTree

	def outline(self, tree, item=None, depth=0):
		"""The labels of the tree with their depth, all branches included."""
		item = item or tree.GetRootItem()
		lines = []
		child, cookie = tree.GetFirstChild(item)
		while child.IsOk():
			lines.append("  " * depth + tree.GetItemText(child))
			lines.extend(self.outline(tree, child, depth + 1))
			child, cookie = tree.GetNextChild(item, cookie)
		return lines

	def focus(self, tree, *path):
		"""Select the item at the path of labels from the root."""
		item = tree.GetRootItem()
		for label in path:
			child, cookie = tree.GetFirstChild(item)
			while tree.GetItemText(child) != label:
				child, cookie = tree.GetNextChild(item, cookie)
			item = child
		tree.SelectItem(item)
		return item

	def press(self, code):
		self.dialog._enterActivatesOk_ctrlSActivatesApply(key(code))


class TestTree(TreeTestCase):
	def test_keys_then_categories_then_scripts(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		self.addScript("Logger", "Stop logging", "kb:NVDA+x")
		self.assertEqual(
			self.outline(self.createTree()),
			[
				"NVDA+X (keyboard, all layouts)",
				"  Logger",
				"    Start logging",
				"    Stop logging",
				"  Tools",
				"    Speech viewer",
			],
		)

	def test_mixed_layouts_are_shown_at_the_keys_and_at_the_scripts(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb(laptop):NVDA+x")
		self.assertEqual(
			self.outline(self.createTree()),
			[
				"NVDA+X (keyboard, all layouts; keyboard, laptop layout)",
				"  Logger",
				"    Start logging (keyboard, laptop layout)",
				"  Tools",
				"    Speech viewer (keyboard, all layouts)",
			],
		)

	def test_gesture_that_nvda_cannot_describe_is_shown_by_its_identifier(self):
		# E.g. the source of the gesture belongs to an add-on that is not running
		self.addScript("Tools", "Speech viewer", "custom(device):k1")
		self.addScript("Logger", "Start logging", "custom(device):k1")
		self.assertEqual(self.outline(self.createTree())[0], "k1 (custom(device))")

	def test_duplicates_are_sorted_and_collapsed_with_the_first_one_selected(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+y", "kb:NVDA+a")
		self.addScript("Logger", "Start logging", "kb:NVDA+y", "kb:NVDA+a")
		tree = self.createTree()
		root = tree.GetRootItem()
		first, cookie = tree.GetFirstChild(root)
		second, cookie = tree.GetNextChild(root, cookie)
		self.assertEqual([tree.GetItemText(first), tree.GetItemText(second)], ["NVDA+A (keyboard, all layouts)", "NVDA+Y (keyboard, all layouts)"])
		self.assertFalse(tree.IsExpanded(first) or tree.IsExpanded(second))
		self.assertEqual(tree.GetSelection(), first)

	def test_enter_on_a_branch_expands_and_collapses_it(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		tree = self.createTree()
		branch = tree.GetFocusedItem()
		self.press(wx.WXK_RETURN)
		self.assertTrue(tree.IsExpanded(branch))
		self.press(wx.WXK_NUMPAD_ENTER)
		self.assertFalse(tree.IsExpanded(branch))
		self.assertEqual(self.dialogs(), [])

	def test_gesture_in_focus(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		tree = self.createTree()
		self.assertIsNone(self.dialog.gestureInFocus())
		self.focus(tree, "NVDA+X (keyboard, all layouts)", "Tools", "Speech viewer")
		self.assertEqual(self.dialog.gestureInFocus().displayName, "Speech viewer")


class TestOpenGesture(TreeTestCase):
	def setUp(self):
		super().setUp()
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		self.tree = self.createTree()

	def test_enter_on_a_script_opens_it_in_the_input_gestures_dialog(self):
		self.focus(self.tree, "NVDA+X (keyboard, all layouts)", "Tools", "Speech viewer")
		self.press(wx.WXK_RETURN)
		(dialog,) = self.dialogs()
		self.assertEqual(dialog[1], "InputGesturesDialogWithSearch")
		self.assertEqual(dialog[2]["search"], "Speech viewer")
		self.assertEqual(dialog[2]["gesture"].gesture, "kb:NVDA+x")

	def test_ok_remembers_the_shown_duplicates(self):
		self.dialog.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK))
		self.assertEqual(
			configuration.getKnownDuplicates(),
			{"kb:NVDA+x globalCommands.GlobalCommands.speechviewer", "kb:NVDA+x globalCommands.GlobalCommands.startlogging"},
		)
		# OK on a branch only closes the window
		self.assertEqual(self.dialogs(), [])

	def test_cancel_does_not_remember_the_duplicates(self):
		self.dialog.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_CANCEL))
		self.assertEqual(configuration.getKnownDuplicates(), set())

	def test_check_box_turns_off_the_search_on_startup_at_once(self):
		self.assertFalse(self.dialog.noStartupCheck.GetValue())
		self.dialog.noStartupCheck.SetValue(True)
		self.dialog.onNoStartupCheck(None)
		self.assertFalse(configuration.isCheckOnStartup())

	def test_check_box_shows_the_saved_option(self):
		configuration.setCheckOnStartup(False)
		self.createTree()
		self.assertTrue(self.dialog.noStartupCheck.GetValue())


class TestUnsignedDuplicate(TreeTestCase):
	def test_warning_for_a_script_without_description(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addUnsignedScript("globalPlugins.example", "hidden", "kb:NVDA+x")
		tree = self.createTree()
		self.focus(tree, "NVDA+X (keyboard, all layouts)", "[globalPlugins.example]", "hidden")
		self.press(wx.WXK_RETURN)
		self.assertEqual(events, [("message", "This gesture is not represented in the NVDA Input Gestures dialog.", "Gesture without description")])
		self.assertEqual(configuration.getKnownDuplicates(), set())


class TestUnsignedList(AddonTestCase):
	def test_gestures_without_description_in_a_list(self):
		self.addUnsignedScript("globalPlugins.example", "second", "kb:NVDA+z")
		self.addUnsignedScript("globalPlugins.example", "first", "kb:NVDA+b")
		dialog = self.createDialog(graphui.UnsignedGesturesDialog, addon.Unsigned())
		gestures = dialog.gesturesList
		self.assertEqual(
			[gestures.GetItemText(row, 1) for row in range(gestures.GetItemCount())],
			["first", "second"],
		)
		self.assertEqual(gestures.GetItemText(0, 0), "NVDA+B (keyboard, all layouts)")
		self.assertEqual(dialog.gestureInFocus().scriptName, "first")


class TestSelectGesture(AddonTestCase):
	def createInputGestures(self, filteredGestures):
		dialog = graphui.InputGesturesDialogWithSearch(None)
		dialog.gesturesVM.filteredGestures = filteredGestures
		return dialog

	def model(self):
		gestureVM = types.SimpleNamespace(normalizedGestureIdentifier="kb:NVDA+x")
		otherVM = types.SimpleNamespace(normalizedGestureIdentifier="kb:NVDA+y")
		info = types.SimpleNamespace(scriptName="speechviewer", moduleName="globalCommands", className="GlobalCommands")
		scriptVM = types.SimpleNamespace(scriptInfo=info, gestures=[otherVM, gestureVM])
		categoryVM = types.SimpleNamespace(displayName="Tools", scripts=[scriptVM])
		return categoryVM, scriptVM, gestureVM

	def gesture(self):
		return self.base.Gesture("kb:NVDA+x", "Tools", "Speech viewer", "GlobalCommands", "globalCommands", "speechviewer")

	def test_the_gesture_itself_is_selected(self):
		categoryVM, scriptVM, gestureVM = self.model()
		dialog = self.createInputGestures([categoryVM])
		events.clear()
		dialog.selectGesture(self.gesture())
		self.assertEqual(events, [("select", (categoryVM, scriptVM, gestureVM))])

	def test_search_and_selection_when_the_dialog_opens(self):
		categoryVM, scriptVM, gestureVM = self.model()
		self.patch(graphui.InputGesturesDialog, "__init__", self.fakeInit([categoryVM]))
		graphui.InputGesturesDialogWithSearch(None, search="Speech viewer", gesture=self.gesture())
		self.assertEqual(events, [("filter", "Speech viewer"), ("select", (categoryVM, scriptVM, gestureVM))])

	def fakeInit(self, filteredGestures):
		original = graphui.InputGesturesDialog.__init__

		def init(dialog, parent, *args, **kwargs):
			original(dialog, parent)
			dialog.gesturesVM.filteredGestures = filteredGestures

		return init

	def test_script_of_another_module_with_the_same_name_is_skipped(self):
		categoryVM, scriptVM, gestureVM = self.model()
		info = types.SimpleNamespace(scriptName="speechviewer", moduleName="globalPlugins.other", className="GlobalPlugin")
		otherScriptVM = types.SimpleNamespace(scriptInfo=info, gestures=[gestureVM])
		categoryVM.scripts.insert(0, otherScriptVM)
		dialog = self.createInputGestures([categoryVM])
		events.clear()
		dialog.selectGesture(self.gesture())
		self.assertEqual(events, [("select", (categoryVM, scriptVM, gestureVM))])

	def test_removed_gesture_selects_its_script(self):
		categoryVM, scriptVM, _gestureVM = self.model()
		scriptVM.gestures = []
		dialog = self.createInputGestures([categoryVM])
		events.clear()
		dialog.selectGesture(self.gesture())
		self.assertEqual(events, [("select", (categoryVM, scriptVM, None))])

	def test_only_the_search_result_if_the_script_is_not_found(self):
		dialog = self.createInputGestures([])
		events.clear()
		dialog.selectGesture(self.gesture())
		self.assertEqual(events, [])
		self.assertTrue(any("not found" in warning for warning in log.warnings))

	def test_only_the_search_result_if_nvda_has_changed_its_dialog(self):
		dialog = self.createInputGestures([])
		del dialog.gesturesVM
		dialog.selectGesture(self.gesture())
		self.assertTrue(any("Unable to select" in warning for warning in log.warnings))

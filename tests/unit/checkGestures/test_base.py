# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

"""The collections of gestures: the scan of NVDA, the duplicates in the keyboard layouts and their groups."""

from checkGesturesSupport import conf
from checkGesturesSupport.case import AddonTestCase


class TestGestures(AddonTestCase):
	def test_gestures_of_the_input_gestures_dialog(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x", "kb(laptop):NVDA+y")
		gestures = self.base.Gestures()
		gestures.signed()
		self.assertEqual([gesture.gesture for gesture in gestures], ["kb:NVDA+x", "kb(laptop):NVDA+y"])
		self.assertEqual(gestures[0].category, "Tools")
		self.assertFalse(gestures[0].isUnsigned)

	def test_gestures_without_description(self):
		self.addUnsignedScript("globalPlugins.example", "hidden", "kb:NVDA+z")
		gestures = self.base.Gestures()
		gestures.unsigned()
		gesture = gestures[0]
		self.assertEqual((gesture.gesture, gesture.scriptName, gesture.moduleName), ("kb:NVDA+z", "hidden", "globalPlugins.example"))
		self.assertTrue(gesture.isUnsigned)
		self.assertEqual(gesture.categoryLabel, "[globalPlugins.example]")

	def test_gestures_of_the_program_in_focus(self):
		import inputCore

		self.base.Gestures().signed()
		self.assertEqual(inputCore.manager.requestedFor[-1], (None, None))

	def test_gestures_of_the_program_that_had_the_focus_before_the_nvda_menu(self):
		import gui
		import inputCore

		self.patch(gui.mainFrame, "prevFocus", "word")
		self.patch(gui.mainFrame, "prevFocusAncestors", ["desktop"])
		self.base.Gestures().signed()
		self.assertEqual(inputCore.manager.requestedFor[-1], ("word", ["desktop"]))

	def test_the_same_gesture_is_added_once(self):
		gestures = self.base.Gestures()
		gestures.append(self.base.Gesture("kb:NVDA+x", "Tools", "Speech viewer", "C", "m", "s"))
		gestures.append(self.base.Gesture("kb:NVDA+x", "Tools", "Speech viewer", "C", "m", "s"))
		self.assertEqual(len(gestures), 1)


class TestDuplicates(AddonTestCase):
	def duplicates(self):
		return [gesture.gesture for gesture in self.base.Duplicates()]

	def test_the_same_keys_of_two_scripts(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		self.addScript("Tools", "Python console", "kb:NVDA+p")
		self.assertEqual(sorted(self.duplicates()), ["kb:NVDA+x", "kb:NVDA+x"])

	def test_all_layouts_and_the_current_layout_are_a_duplicate(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb(laptop):NVDA+x")
		self.assertEqual(len(self.duplicates()), 2)

	def test_other_layout_is_not_a_duplicate(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb(desktop):NVDA+x")
		self.assertEqual(self.duplicates(), [])

	def test_both_specific_layouts_are_not_a_duplicate(self):
		self.addScript("Tools", "Speech viewer", "kb(laptop):NVDA+x")
		self.addScript("Logger", "Start logging", "kb(desktop):NVDA+x")
		self.assertEqual(self.duplicates(), [])

	def test_current_layout_changes_the_duplicates(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb(desktop):NVDA+x")
		conf["keyboard"]["keyboardLayout"] = "desktop"
		self.assertEqual(len(self.duplicates()), 2)

	def test_script_without_description_with_the_same_keys(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addUnsignedScript("globalPlugins.example", "hidden", "kb:NVDA+x")
		self.assertEqual(len(self.duplicates()), 2)


class TestGroups(AddonTestCase):
	def test_one_group_for_each_duplicate(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x", "kb:NVDA+y")
		self.addScript("Logger", "Start logging", "kb(laptop):NVDA+x")
		self.addScript("Browse mode", "Find", "kb:NVDA+y")
		groups = self.base.Duplicates().groups()
		self.assertEqual([group.key for group in groups], ["kb:NVDA+x", "kb:NVDA+y"])
		self.assertEqual(len(groups[0].gestures), 2)

	def test_categories_and_scripts_are_sorted_by_name(self):
		self.addScript("tools", "b script", "kb:NVDA+x")
		self.addScript("tools", "A script", "kb:NVDA+x")
		self.addScript("Browse mode", "Find", "kb:NVDA+x")
		self.addUnsignedScript("globalPlugins.example", "hidden", "kb:NVDA+x")
		group = self.base.Duplicates().groups()[0]
		categories = group.categories()
		self.assertEqual([category for category, _gestures in categories], ["[globalPlugins.example]", "Browse mode", "tools"])
		self.assertEqual([gesture.displayName for gesture in categories[2][1]], ["A script", "b script"])

	def test_signatures_do_not_depend_on_the_description(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x", scriptName="speechViewer")
		self.addScript("Logger", "Start logging", "kb:NVDA+x", scriptName="log", moduleName="globalPlugins.logger", className="GlobalPlugin")
		signatures = self.base.getSignatures(self.base.Duplicates().groups())
		self.assertEqual(
			signatures,
			{"kb:NVDA+x globalCommands.GlobalCommands.speechViewer", "kb:NVDA+x globalPlugins.logger.GlobalPlugin.log"},
		)

	def test_no_duplicates(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.assertEqual(self.base.Duplicates().groups(), [])
		self.assertEqual(len(self.base.Duplicates()), 0)

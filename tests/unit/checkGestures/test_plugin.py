# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

"""The global plugin: its menu, its commands and the search for new duplicates after NVDA has started."""

from checkGesturesSupport import addon, appArgs, events, later, module, postNvdaStartup, runLater
from checkGesturesSupport.case import AddonTestCase

configuration = module("configuration")


class TestMenu(AddonTestCase):
	def test_menu_items(self):
		import gui

		bound = gui.mainFrame.sysTrayIcon.bound[-3:]
		self.assertEqual(
			bound,
			[
				("onCheckDuplicates", "Search for duplicate gestures..."),
				("onCheckUnsigned", "Gestures without description..."),
				("onHelp", "Help"),
			],
		)

	def test_descriptions_of_the_commands(self):
		self.assertEqual(addon.GlobalPlugin.script_duplicates.__doc__, "Search for duplicate gestures")
		self.assertEqual(addon.GlobalPlugin.script_unsigned.__doc__, "Gestures without description")


class TestSearchFromTheMenu(AddonTestCase):
	def test_all_duplicates_are_shown(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		configuration.rememberDuplicates(configuration.getKnownDuplicates() | {"kb:NVDA+x globalCommands.GlobalCommands.speechviewer", "kb:NVDA+x globalCommands.GlobalCommands.startlogging"})
		self.plugin.onCheckDuplicates(None)
		self.assertEqual([event[1] for event in self.dialogs()], ["DuplicatedGesturesDialog"])

	def test_message_without_duplicates(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.plugin.onCheckDuplicates(None)
		self.assertEqual(events, [("message", "Target gestures not found", "Search for duplicate gestures")])

	def test_gestures_without_description(self):
		self.addUnsignedScript("globalPlugins.example", "hidden", "kb:NVDA+z")
		self.plugin.onCheckUnsigned(None)
		self.assertEqual([event[1] for event in self.dialogs()], ["UnsignedGesturesDialog"])

	def test_the_menu_does_not_remember_the_duplicates(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")
		self.plugin.onCheckDuplicates(None)
		self.assertEqual(configuration.getKnownDuplicates(), set())


class TestSearchOnStartup(AddonTestCase):
	def addDuplicate(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.addScript("Logger", "Start logging", "kb:NVDA+x")

	def startNvda(self):
		events.clear()
		postNvdaStartup.notify()
		runLater()

	def test_search_runs_5_seconds_after_nvda_has_started(self):
		postNvdaStartup.notify()
		self.assertEqual(events, [("later", 5000, "checkOnStartup")])

	def test_new_duplicates_are_shown(self):
		self.addDuplicate()
		self.startNvda()
		self.assertEqual([event[1] for event in self.dialogs()], ["DuplicatedGesturesDialog"])

	def test_known_duplicates_are_not_shown(self):
		self.addDuplicate()
		configuration.rememberDuplicates(self.base.getSignatures(self.base.Duplicates().groups()))
		self.startNvda()
		self.assertEqual(self.dialogs(), [])

	def test_a_new_script_with_known_keys_is_a_new_duplicate(self):
		self.addDuplicate()
		configuration.rememberDuplicates(self.base.getSignatures(self.base.Duplicates().groups()))
		self.addScript("Browse mode", "Find", "kb:NVDA+x")
		self.startNvda()
		self.assertEqual(len(self.dialogs()), 1)

	def test_without_duplicates_nothing_is_shown(self):
		self.addScript("Tools", "Speech viewer", "kb:NVDA+x")
		self.startNvda()
		# Only the delayed search itself, neither a window nor a message
		self.assertEqual([event for event in events if event[0] != "later"], [])

	def test_resolved_duplicates_are_forgotten(self):
		configuration.rememberDuplicates({"kb:NVDA+q old.Old.removed"})
		self.startNvda()
		self.assertEqual(configuration.getKnownDuplicates(), set())

	def test_not_searched_when_it_is_turned_off(self):
		self.addDuplicate()
		configuration.setCheckOnStartup(False)
		self.startNvda()
		self.assertEqual(self.dialogs(), [])

	def test_not_registered_on_secure_screens(self):
		self.plugin.terminate()
		appArgs.secure = True
		self.plugin = addon.GlobalPlugin()
		self.assertEqual(postNvdaStartup.handlers, [])

	def test_unregistered_when_the_plugin_ends(self):
		self.plugin.terminate()
		self.assertEqual(postNvdaStartup.handlers, [])
		self.assertEqual(later, [])
		# A new plugin for tearDown, which ends the plugin of the test
		self.plugin = addon.GlobalPlugin()

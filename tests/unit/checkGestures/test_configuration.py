# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

"""The data of the add-on in its own file: saved at once, whatever NVDA does with its configuration."""

import json

from checkGesturesSupport import appArgs, log, module
from checkGesturesSupport.case import DATA_FILE, AddonTestCase

configuration = module("configuration")


class TestConfiguration(AddonTestCase):
	def test_defaults_without_the_file(self):
		self.assertTrue(configuration.isCheckOnStartup())
		self.assertEqual(configuration.getKnownDuplicates(), set())

	def test_values_are_saved_in_the_file_at_once(self):
		self.patch(configuration, "_today", lambda: "2026-10-24")
		configuration.rememberDuplicates({"kb:NVDA+x a.B.c", "kb:NVDA+x d.E.f"})
		configuration.setCheckOnStartup(False)
		with open(DATA_FILE, encoding="utf-8") as file:
			data = json.load(file)
		self.assertEqual(
			data,
			{"knownDuplicates": {"kb:NVDA+x a.B.c": "2026-10-24", "kb:NVDA+x d.E.f": "2026-10-24"}, "checkOnStartup": False},
		)
		self.assertFalse(configuration.isCheckOnStartup())
		self.assertEqual(configuration.getKnownDuplicates(), {"kb:NVDA+x a.B.c", "kb:NVDA+x d.E.f"})

	def test_seen_duplicates_are_added_to_the_saved_ones(self):
		configuration.rememberDuplicates({"kb:NVDA+x a.B.c"})
		configuration.rememberDuplicates({"kb:NVDA+y d.E.f"})
		self.assertEqual(configuration.getKnownDuplicates(), {"kb:NVDA+x a.B.c", "kb:NVDA+y d.E.f"})

	def test_the_same_duplicates_are_not_written_again(self):
		configuration.rememberDuplicates({"kb:NVDA+x a.B.c"})
		saved = []
		self.patch(configuration, "_save", lambda **values: saved.append(values))
		configuration.rememberDuplicates({"kb:NVDA+x a.B.c"})
		self.assertEqual(saved, [])

	def test_list_of_the_first_builds_is_read_and_saved_in_the_current_format(self):
		self.patch(configuration, "_today", lambda: "2026-10-24")
		with open(DATA_FILE, "w", encoding="utf-8") as file:
			json.dump({"knownDuplicates": ["kb:NVDA+x a.B.c"]}, file)
		self.assertEqual(configuration.getKnownDuplicates(), {"kb:NVDA+x a.B.c"})
		configuration.updateKnownDuplicates(set())
		with open(DATA_FILE, encoding="utf-8") as file:
			self.assertEqual(json.load(file)["knownDuplicates"], {"kb:NVDA+x a.B.c": "2026-10-24"})


	def test_damaged_file_gives_the_defaults(self):
		with open(DATA_FILE, "w", encoding="utf-8") as file:
			file.write("{not json")
		self.assertTrue(configuration.isCheckOnStartup())
		self.assertTrue(log.errors)

	def test_nothing_is_saved_on_secure_screens(self):
		appArgs.secure = True
		configuration.setCheckOnStartup(False)
		configuration.rememberDuplicates({"kb:NVDA+x a.B.c"})
		appArgs.secure = False
		self.assertTrue(configuration.isCheckOnStartup())
		self.assertEqual(configuration.getKnownDuplicates(), set())


class TestForgetDuplicates(AddonTestCase):
	GLOBAL = "kb:NVDA+x globalCommands.GlobalCommands.speechViewer"
	PLUGIN = "kb:NVDA+x globalPlugins.logger.GlobalPlugin.log"
	PROGRAM = "kb:NVDA+q appModules.explorer.AppModule.rename"

	def setUp(self):
		super().setUp()
		self.today = "2026-01-01"
		self.patch(configuration, "_today", lambda: self.today)
		configuration.rememberDuplicates({self.GLOBAL, self.PLUGIN, self.PROGRAM})

	def saved(self):
		with open(DATA_FILE, encoding="utf-8") as file:
			return json.load(file)["knownDuplicates"]

	def test_found_duplicates_get_the_current_date(self):
		self.today = "2026-03-01"
		configuration.updateKnownDuplicates({self.GLOBAL, self.PLUGIN, self.PROGRAM})
		self.assertEqual(set(self.saved().values()), {"2026-03-01"})

	def test_global_duplicates_are_forgotten_at_once(self):
		configuration.updateKnownDuplicates({self.PLUGIN})
		self.assertEqual(configuration.getKnownDuplicates(), {self.PLUGIN, self.PROGRAM})
		configuration.updateKnownDuplicates(set())
		self.assertEqual(configuration.getKnownDuplicates(), {self.PROGRAM})

	def test_duplicates_of_the_focus_are_kept_for_90_days(self):
		self.today = "2026-04-01"
		configuration.updateKnownDuplicates(set())
		self.assertEqual(configuration.getKnownDuplicates(), {self.PROGRAM})

	def test_duplicates_of_the_focus_are_forgotten_after_90_days(self):
		self.today = "2026-04-02"
		configuration.updateKnownDuplicates(set())
		self.assertEqual(configuration.getKnownDuplicates(), set())

	def test_new_duplicates_are_not_added_by_a_search(self):
		configuration.updateKnownDuplicates({self.GLOBAL, self.PLUGIN, self.PROGRAM, "kb:NVDA+z globalCommands.GlobalCommands.new"})
		self.assertEqual(configuration.getKnownDuplicates(), {self.GLOBAL, self.PLUGIN, self.PROGRAM})

	def test_unreadable_date_is_kept(self):
		with open(DATA_FILE, "w", encoding="utf-8") as file:
			json.dump({"knownDuplicates": {self.PROGRAM: "yesterday"}}, file)
		configuration.updateKnownDuplicates(set())
		self.assertEqual(configuration.getKnownDuplicates(), {self.PROGRAM})

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
		configuration.rememberDuplicates({"kb:NVDA+x a.B.c", "kb:NVDA+x d.E.f"})
		configuration.setCheckOnStartup(False)
		with open(DATA_FILE, encoding="utf-8") as file:
			data = json.load(file)
		self.assertEqual(data, {"knownDuplicates": ["kb:NVDA+x a.B.c", "kb:NVDA+x d.E.f"], "checkOnStartup": False})
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

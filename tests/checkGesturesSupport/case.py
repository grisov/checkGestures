# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

"""The base class of the tests: the gestures of NVDA given by each test and a fresh global plugin."""

from __future__ import annotations
import os
import types
import unittest
from typing import Any

import wx

from . import FakeScriptInfo, addon, appArgs, conf, configPath, events, later, log, mappings, module, runningPlugins

DATA_FILE = os.path.join(configPath, "checkGestures.json")


class AddonTestCase(unittest.TestCase):
	"""Every test starts without gestures, without the saved data of the add-on and with a new global plugin."""

	def setUp(self) -> None:
		self._patches: list[tuple[Any, str, Any]] = []
		mappings.clear()
		runningPlugins.clear()
		events.clear()
		later.clear()
		log.clear()
		conf["keyboard"]["keyboardLayout"] = "laptop"
		appArgs.secure = False
		if os.path.exists(DATA_FILE):
			os.remove(DATA_FILE)
		# The delayed selection in the Input Gestures dialog runs at once in the tests
		self.patch(wx, "CallAfter", lambda function, *args: function(*args))
		self.plugin = addon.GlobalPlugin()
		events.clear()

	def tearDown(self) -> None:
		self.plugin.terminate()
		for target, name, original in reversed(self._patches):
			setattr(target, name, original)
		for window in wx.GetTopLevelWindows():
			window.Destroy()

	def patch(self, target: Any, name: str, value: Any) -> None:
		"""Replace an attribute for this test only."""
		self._patches.append((target, name, getattr(target, name)))
		setattr(target, name, value)

	def addScript(
		self,
		category: str,
		displayName: str,
		*gestures: str,
		scriptName: str = "",
		moduleName: str = "globalCommands",
		className: str = "GlobalCommands",
	) -> FakeScriptInfo:
		"""Add a script with its gestures, as it is shown in the Input Gestures dialog."""
		info = FakeScriptInfo(
			category,
			displayName,
			scriptName or displayName.lower().replace(" ", ""),
			list(gestures),
			moduleName,
			className,
		)
		mappings.setdefault(category, {})[displayName] = info
		return info

	def addUnsignedScript(self, moduleName: str, scriptName: str, *gestures: str) -> None:
		"""Add a script without a description to a running global plugin, it is not in the Input Gestures dialog."""

		def script(self: Any, gesture: Any) -> None:
			pass

		script.__name__ = f"script_{scriptName}"
		script.__module__ = moduleName
		script.__doc__ = None
		runningPlugins.append(types.SimpleNamespace(_gestureMap={gesture: script for gesture in gestures}))

	def dialogs(self) -> list[Any]:
		"""The dialogs shown by the add-on since the start of the test."""
		return [event for event in events if event[0] == "dialog"]

	def createDialog(self, dialogClass: Any, gestures: Any) -> Any:
		"""Create a window of the add-on as NVDA does, without showing it."""
		return dialogClass(None, title=gestures.title, gestures=gestures)

	@property
	def base(self) -> types.ModuleType:
		return module("base")

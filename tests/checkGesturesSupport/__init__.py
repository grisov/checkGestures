# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

"""Loads the add-on outside NVDA for the tests of the add-on.

The modules of NVDA are replaced with small stand-ins that record what the add-on does (shown dialogs,
messages, delayed calls), and the gestures of NVDA are given by the tests. wxPython is the real one,
so the windows of the add-on are built with real controls without being shown.
The tests run only on Windows and are skipped elsewhere, e.g. in the tests workflow on Linux.
"""

from __future__ import annotations
import builtins
from abc import ABCMeta
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from typing import Any

if sys.platform != "win32":
	raise unittest.SkipTest("the tests of the add-on need Windows and wxPython")

import wx  # noqa: E402

ADDON_DIR = Path(__file__).parents[2] / "addon" / "globalPlugins" / "checkGestures"
PACKAGE = "checkGestures"

# The wx application needed by the real controls
app = wx.App(False)

# What the add-on did, inspected by the tests: shown dialogs and messages, delayed calls
events: list[Any] = []
# The calls delayed with core.callLater, run by the tests with runLater()
later: list[tuple[int, Any, tuple[Any, ...]]] = []
# The gestures of NVDA: the mappings shown in the Input Gestures dialog and the running global plugins
mappings: dict[str, dict[str, Any]] = {}
runningPlugins: list[Any] = []
# The NVDA configuration folder, where the add-on saves its file
configPath = tempfile.mkdtemp(prefix="checkGestures-tests-")
appArgs = types.SimpleNamespace(secure=False, configPath=configPath)
conf: dict[str, Any] = {"keyboard": {"keyboardLayout": "laptop"}}


class _Log:
	"""Collects the errors and debug warnings logged by the add-on."""

	def __init__(self) -> None:
		self.errors: list[str] = []
		self.warnings: list[str] = []

	def error(self, message: str, *args: Any, **kwargs: Any) -> None:
		self.errors.append(message)

	def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
		self.warnings.append(message)

	def debugWarning(self, message: str, *args: Any, **kwargs: Any) -> None:
		self.warnings.append(message)

	def clear(self) -> None:
		self.errors.clear()
		self.warnings.clear()


log = _Log()


class _Action:
	"""Stands for extensionPoints.Action."""

	def __init__(self) -> None:
		self.handlers: list[Any] = []

	def register(self, handler: Any) -> None:
		self.handlers.append(handler)

	def unregister(self, handler: Any) -> bool:
		if handler in self.handlers:
			self.handlers.remove(handler)
			return True
		return False

	def notify(self, **kwargs: Any) -> None:
		for handler in list(self.handlers):
			handler(**kwargs)


postNvdaStartup = _Action()


def _callLater(delay: int, function: Any, *args: Any) -> None:
	"""Stands for core.callLater: keeps the call for runLater() and records the delay among the events."""
	events.append(("later", delay, function.__name__))
	later.append((delay, function, args))


def runLater() -> None:
	"""Run the calls delayed with core.callLater so far."""
	pending = list(later)
	later.clear()
	for _delay, function, args in pending:
		function(*args)


class _GlobalPlugin:
	"""Stands for globalPluginHandler.GlobalPlugin."""

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		pass

	def terminate(self) -> None:
		pass


def _script(description: str = "", **kwargs: Any) -> Any:
	"""Stands for scriptHandler.script: the description becomes the docstring, as in NVDA."""

	def decorate(function: Any) -> Any:
		if description:
			function.__doc__ = description
		return function

	return decorate


_SOURCES = {
	"kb": "keyboard, all layouts",
	"kb(laptop)": "keyboard, laptop layout",
	"kb(desktop)": "keyboard, desktop layout",
	"br(freedomScientific)": "Freedom Scientific braille displays",
}


def getDisplayTextForGestureIdentifier(identifier: str) -> tuple[str, str]:
	"""Stands for inputCore.getDisplayTextForGestureIdentifier, e.g. ("keyboard, all layouts", "NVDA+Shift+L")."""
	device, keys = identifier.split(":", 1)
	return _SOURCES[device], "+".join(key if key == "NVDA" else key.capitalize() for key in keys.split("+"))


class FakeScriptInfo:
	"""inputCore.AllGesturesScriptInfo: a script with its gestures in the Input Gestures dialog."""

	def __init__(
		self,
		category: str,
		displayName: str,
		scriptName: str,
		gestures: list[str],
		moduleName: str = "globalCommands",
		className: str = "GlobalCommands",
	) -> None:
		self.category, self.displayName, self.scriptName = category, displayName, scriptName
		self.gestures, self.moduleName, self.className = gestures, moduleName, className


class _Manager:
	def getAllGestureMappings(self) -> dict[str, dict[str, Any]]:
		return mappings


class _SysTrayIcon:
	"""The tray icon of NVDA with its real tools menu; the bound menu items are recorded."""

	def __init__(self) -> None:
		self.toolsMenu = wx.Menu()
		self.bound: list[Any] = []

	def Bind(self, event: Any, handler: Any, item: Any) -> None:
		self.bound.append((handler.__name__, item.GetItemLabelText()))


class _MainFrame:
	"""gui.mainFrame: the shown settings dialogs are recorded, not created."""

	def __init__(self) -> None:
		self.sysTrayIcon = _SysTrayIcon()

	def popupSettingsDialog(self, dialog: Any, *args: Any, **kwargs: Any) -> None:
		events.append(("dialog", dialog.__name__, kwargs))


def _messageBox(message: str, caption: str = "", style: int = 0, parent: Any = None) -> int:
	events.append(("message", message, caption))
	return wx.OK


class SIPABCMeta(type(wx.Dialog), ABCMeta):
	"""gui.guiHelper.SIPABCMeta: the metaclass of the settings dialogs of NVDA, which may have abstract methods."""


class FakeSettingsDialog(wx.Dialog, metaclass=SIPABCMeta):
	"""gui.settingsDialogs.SettingsDialog on a real wx dialog: makeSettings and postInit are called as in NVDA,
	and the OK and Cancel buttons call onOk and onCancel.
	"""

	title = ""

	def __init__(self, parent: Any, *args: Any, **kwargs: Any) -> None:
		super().__init__(parent, title=self.title)
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
		self.makeSettings(wx.BoxSizer(wx.VERTICAL))
		self.postInit()

	def makeSettings(self, sizer: Any) -> None:
		pass

	def postInit(self) -> None:
		pass

	def _enterActivatesOk_ctrlSActivatesApply(self, evt: Any) -> None:
		pass

	def onOk(self, evt: Any) -> None:
		self.Destroy()

	def onCancel(self, evt: Any) -> None:
		self.Destroy()


class FakeBoxSizerHelper:
	"""gui.guiHelper.BoxSizerHelper: the controls are created with the dialog as their parent."""

	def __init__(self, parent: Any, sizer: Any = None, **kwargs: Any) -> None:
		self.parent, self.sizer = parent, sizer
		self.labels: list[str] = []

	def addItem(self, item: Any, **kwargs: Any) -> Any:
		return item

	def addLabeledControl(self, label: str, controlClass: Any, **kwargs: Any) -> Any:
		self.labels.append(label)
		return controlClass(self.parent, **kwargs)


class FakeAutoWidthColumnListCtrl(wx.ListCtrl):
	"""gui.nvdaControls.AutoWidthColumnListCtrl on a real wx list."""

	def __init__(self, parent: Any, autoSizeColumn: Any = None, itemTextCallable: Any = None, **kwargs: Any) -> None:
		super().__init__(parent, **kwargs)


class FakeInputGesturesDialog:
	"""gui.inputGestures.InputGesturesDialog with its filter, its internal view model and tree."""

	def __init__(self, parent: Any, *args: Any, **kwargs: Any) -> None:
		self.filterCtrl = types.SimpleNamespace(SetValue=lambda text: events.append(("filter", text)))
		self.gesturesVM = types.SimpleNamespace(filteredGestures=[])
		self.tree = types.SimpleNamespace(doRefresh=lambda focus=None: events.append(("select", focus)))


def _module(name: str, **attributes: Any) -> types.ModuleType:
	module = types.ModuleType(name)
	module.__dict__.update(attributes)
	sys.modules[name] = module
	return module


def _installNvda() -> None:
	"""Replace the modules of NVDA used by the add-on."""
	_module(
		"addonHandler",
		initTranslation=lambda: None,
		AddonError=Exception,
		getCodeAddon=lambda: types.SimpleNamespace(
			manifest={"name": PACKAGE, "summary": "Check Input Gestures"},
			getDocFilePath=lambda: "readme.html",
		),
	)
	_module("config", conf=conf, isAppX=False)
	_module("core", callLater=_callLater, postNvdaStartup=postNvdaStartup)
	_module("globalPluginHandler", GlobalPlugin=_GlobalPlugin, runningPlugins=runningPlugins)
	_module("globalVars", appArgs=appArgs)
	_module(
		"inputCore",
		InputGesture=object,
		manager=_Manager(),
		getDisplayTextForGestureIdentifier=getDisplayTextForGestureIdentifier,
	)
	_module("logHandler", log=log)
	_module("scriptHandler", script=_script)
	settingsDialogs = _module("gui.settingsDialogs", SettingsDialog=FakeSettingsDialog)
	guiHelper = _module("gui.guiHelper", BoxSizerHelper=FakeBoxSizerHelper)
	nvdaControls = _module("gui.nvdaControls", AutoWidthColumnListCtrl=FakeAutoWidthColumnListCtrl)
	inputGestures = _module("gui.inputGestures", InputGesturesDialog=FakeInputGesturesDialog)
	_module(
		"gui",
		mainFrame=_MainFrame(),
		messageBox=_messageBox,
		settingsDialogs=settingsDialogs,
		guiHelper=guiHelper,
		nvdaControls=nvdaControls,
		inputGestures=inputGestures,
	)
	builtins._ = lambda text: text  # type: ignore[attr-defined]


def _load() -> types.ModuleType:
	"""Load the add-on package once, with the stand-ins of NVDA and the real wxPython."""
	if PACKAGE in sys.modules and getattr(sys.modules[PACKAGE], "__checkGesturesTests__", False):
		return sys.modules[PACKAGE]
	_installNvda()
	# No compiled files in the folder of the add-on: they could get into the package of the add-on
	sys.dont_write_bytecode = True
	spec = importlib.util.spec_from_file_location(
		PACKAGE,
		ADDON_DIR / "__init__.py",
		submodule_search_locations=[str(ADDON_DIR)],
	)
	assert spec is not None and spec.loader is not None
	package = importlib.util.module_from_spec(spec)
	sys.modules[PACKAGE] = package
	spec.loader.exec_module(package)
	sys.dont_write_bytecode = False
	package.__checkGesturesTests__ = True
	return package


addon = _load()


def module(name: str) -> types.ModuleType:
	"""A module of the add-on, e.g. module("base")."""
	return sys.modules[f"{PACKAGE}.{name}"]

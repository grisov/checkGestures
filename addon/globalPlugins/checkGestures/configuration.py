# configuration.py
# The name of the add-on and its data saved in a separate file
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

import json
from os import path
from typing import Any, cast

import addonHandler
from globalVars import appArgs
from logHandler import log

# The manifest of the add-on has no type annotations
_addon = cast(Any, addonHandler).getCodeAddon()
ADDON_NAME: str = _addon.manifest["name"]
ADDON_SUMMARY: str = _addon.manifest["summary"]

# The data of the add-on is saved in its own file in the NVDA configuration folder at once, not in the configuration
# of NVDA: NVDA may be set not to save its configuration on exit, and saving it would save other unsaved changes too.
# appArgs of NVDA has no type annotations
_FILE: str = path.join(cast(Any, appArgs).configPath, ADDON_NAME + ".json")


def _load() -> dict[str, Any]:
	"""Load the saved data of the add-on.
	@return: the data, empty if it has not been saved yet or cannot be read
	@rtype: dict[str, Any]
	"""
	try:
		with open(_FILE, encoding="utf-8") as file:
			data = json.load(file)
	except FileNotFoundError:
		return {}
	except Exception:
		log.error(f"Unable to read {_FILE}", exc_info=True)
		return {}
	return cast(dict[str, Any], data) if isinstance(data, dict) else {}


def _save(**values: Any) -> None:
	"""Save the given values with the other saved data of the add-on, an error is logged.
	Nothing is saved on secure screens, where the configuration of NVDA must not be changed.
	@param values: the names and the values to save
	@type values: Any
	"""
	if cast(Any, appArgs).secure:
		return
	data = _load()
	data.update(values)
	try:
		with open(_FILE, "w", encoding="utf-8") as file:
			json.dump(data, file, ensure_ascii=False, indent="\t")
	except Exception:
		log.error(f"Unable to save {_FILE}", exc_info=True)


def isCheckOnStartup() -> bool:
	"""Whether the new duplicate gestures are searched for and shown after NVDA has started.
	@return: True by default
	@rtype: bool
	"""
	return bool(_load().get("checkOnStartup", True))


def setCheckOnStartup(enabled: bool) -> None:
	"""Turn on or off the search for new duplicate gestures after NVDA has started.
	@param enabled: whether the search is turned on
	@type enabled: bool
	"""
	_save(checkOnStartup=enabled)


def getKnownDuplicates() -> set[str]:
	"""The signatures of the duplicates that the user has seen.
	@return: the signatures, empty if no duplicates have been seen yet
	@rtype: set[str]
	"""
	known = _load().get("knownDuplicates", [])
	return {str(item) for item in cast(list[Any], known)} if isinstance(known, list) else set()


def rememberDuplicates(signatures: set[str]) -> None:
	"""Add the duplicates that the user has seen to the saved ones, so only new duplicates are shown when NVDA starts.
	The duplicates found depend on the focus, e.g. the commands of the program in focus or of browse mode,
	so the duplicates seen before are kept even if they are not found now.
	@param signatures: the signatures of the duplicates
	@type signatures: set[str]
	"""
	known = getKnownDuplicates()
	if not signatures <= known:
		_save(knownDuplicates=sorted(known | signatures))

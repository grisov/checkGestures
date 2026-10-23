# configuration.py
# The name of the add-on and its data saved in a separate file
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

import json
from datetime import date, timedelta
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
# A seen duplicate that depends on the focus, e.g. of the program in focus, is forgotten
# if it has not been found for this number of days
FORGET_AFTER_DAYS = 90
# The modules of the scripts available whatever has the focus: their duplicates are forgotten
# as soon as they are not found
GLOBAL_MODULES = ("globalCommands.", "globalPlugins.")


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


def _today() -> str:
	"""The current date as it is saved for the duplicates.
	@return: the date in the ISO format, e.g. "2026-10-24"
	@rtype: str
	"""
	return date.today().isoformat()


def _loadKnownDuplicates() -> dict[str, str]:
	"""Load the seen duplicates with the dates when they were found last time.
	The list saved by the first builds of version 1.2 is read with the current date.
	@return: the signatures of the duplicates and the dates in the ISO format
	@rtype: dict[str, str]
	"""
	known = _load().get("knownDuplicates", {})
	if isinstance(known, list):
		return {str(item): _today() for item in cast(list[Any], known)}
	if isinstance(known, dict):
		return {str(signature): str(seen) for signature, seen in cast(dict[Any, Any], known).items()}
	return {}


def _isGlobal(signature: str) -> bool:
	"""Whether the duplicate is available whatever has the focus: a command of NVDA or of a global plugin.
	@param signature: the signature of the duplicate, the keys and the script
	@type signature: str
	@return: whether the script of the duplicate is global
	@rtype: bool
	"""
	return signature.partition(" ")[2].startswith(GLOBAL_MODULES)


def _isExpired(seen: str) -> bool:
	"""Whether the duplicate has not been found for too long.
	@param seen: the date when the duplicate was found last time, in the ISO format
	@type seen: str
	@return: whether the duplicate is to be forgotten, False if the date cannot be read
	@rtype: bool
	"""
	try:
		return date.fromisoformat(seen) < date.fromisoformat(_today()) - timedelta(days=FORGET_AFTER_DAYS)
	except ValueError:
		return False


def getKnownDuplicates() -> set[str]:
	"""The signatures of the duplicates that the user has seen.
	@return: the signatures, empty if no duplicates have been seen yet
	@rtype: set[str]
	"""
	return set(_loadKnownDuplicates())


def updateKnownDuplicates(found: set[str]) -> None:
	"""Update the seen duplicates after a search, so the file keeps only the duplicates that still exist:
	the date of each found one is updated, a global one that is not found is forgotten at once,
	and another one is forgotten if it has not been found for FORGET_AFTER_DAYS days.
	The new duplicates are not added here, only when the user has seen them.
	@param found: the signatures of the duplicates found now
	@type found: set[str]
	"""
	known = _loadKnownDuplicates()
	updated: dict[str, str] = {}
	for signature, seen in known.items():
		if signature in found:
			updated[signature] = _today()
		elif not _isGlobal(signature) and not _isExpired(seen):
			updated[signature] = seen
	# The list of the first builds of version 1.2 is saved in the current format too
	if updated != known or isinstance(_load().get("knownDuplicates"), list):
		_save(knownDuplicates=updated)


def rememberDuplicates(signatures: set[str]) -> None:
	"""Add the duplicates that the user has seen to the saved ones, so only new duplicates are shown when NVDA starts.
	The duplicates found depend on the focus, e.g. the commands of the program in focus or of browse mode,
	so the duplicates seen before are kept even if they are not found now.
	@param signatures: the signatures of the duplicates
	@type signatures: set[str]
	"""
	known = _loadKnownDuplicates()
	today = _today()
	updated = known | {signature: today for signature in signatures}
	if updated != known:
		_save(knownDuplicates=updated)

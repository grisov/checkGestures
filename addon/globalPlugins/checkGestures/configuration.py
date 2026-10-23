# configuration.py
# The options of the add-on in the NVDA configuration
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

from collections.abc import MutableMapping
from typing import Any, cast

import addonHandler
import config

# The manifest of the add-on has no type annotations
_addon = cast(Any, addonHandler).getCodeAddon()
ADDON_NAME: str = _addon.manifest["name"]
ADDON_SUMMARY: str = _addon.manifest["summary"]

# The options of the add-on in the NVDA configuration
confspec: dict[str, str] = {
	# Search for duplicate gestures after NVDA has started and show the new ones
	"checkOnStartup": "boolean(default=true)",
	# The duplicates found by the last search, so only new duplicates are shown when NVDA starts
	"knownDuplicates": "string_list(default=list())",
}


def getAddonConfig() -> MutableMapping[str, Any]:
	"""Get the add-on section of the NVDA configuration in the current configuration profile.
	NVDA declares config.conf as None until the configuration is loaded, so its type is given here once.
	@return: the options of the add-on
	@rtype: MutableMapping[str, Any]
	"""
	return cast(Any, config.conf)[ADDON_NAME]


def saveAddonConfig(options: dict[str, Any]) -> None:
	"""Save the options of the add-on in the base configuration profile of NVDA,
	so they apply whatever configuration profile is active.
	@param options: the options of the add-on and their values
	@type options: dict[str, Any]
	"""
	# The configuration profiles of NVDA have no type annotations
	baseProfile = cast(Any, config.conf).profiles[0]
	try:
		baseProfile[ADDON_NAME].update(options)
	except (KeyError, AttributeError):
		baseProfile[ADDON_NAME] = options
	# NVDA caches the values read through config.conf, and a change of a profile itself does not update the cache:
	# the cached section of the add-on is dropped, so the new values apply at once
	cast(Any, config.conf).rootSection._cache.pop(ADDON_NAME, None)

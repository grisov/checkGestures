# base.py
# Components required to work with input gestures collection
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021-2026 Oleksandr Gryshchenko <grisov.nvaccess@mailgw.com>

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, cast, override


class Gesture:
	"""Representation of one input gesture."""

	def __init__(
		self,
		gesture: str,
		category: str | None = None,
		displayName: str | None = None,
		className: str | None = None,
		moduleName: str | None = None,
		scriptName: str | None = None,
	) -> None:
		"""Initialization of the main fields of the gesture description.
		@param gesture: text representation of the input gesture
		@type gesture: str
		@param category: the category to which the gesture-related function belongs
		@type category: str | None
		@param displayName: description of the gesture-related function
		@type displayName: str | None
		@param className: the name of the class to which the gesture-related function belongs
		@type className: str | None
		@param moduleName: the name of the module to which the associated class belongs
		@type moduleName: str | None
		@param scriptName: the script name of the gesture-bound function
		@type scriptName: str | None
		"""
		super().__init__()
		self._gesture = gesture or ""
		self._category = category or ""
		self._displayName = displayName or ""
		self._className = className or ""
		self._moduleName = moduleName or ""
		self._scriptName = scriptName or ""

	@property
	def gesture(self) -> str:
		"""String presentation of the input gesture.
		@return: input gesture or empty string
		@rtype: str
		"""
		return self._gesture

	@property
	def category(self) -> str:
		"""The category to which the gesture-bound function belongs.
		@return: the name of the category of the bound function or empty string
		@rtype: str
		"""
		return self._category

	@property
	def categoryLabel(self) -> str:
		"""The category shown for the gesture: a gesture without a category is not shown in the Input Gestures dialog,
		so the name of its module is shown in square brackets instead.
		@return: the category or the module name in square brackets
		@rtype: str
		"""
		return self._category or f"[{self._moduleName}]"

	@property
	def isUnsigned(self) -> bool:
		"""Whether the gesture is not shown in the NVDA Input Gestures dialog, because its script has no description.
		@return: whether the gesture has no category
		@rtype: bool
		"""
		return not self._category

	@property
	def displayName(self) -> str:
		"""Text description of the gesture-bound feature.
		@return: text description of the function or empty stringn
		@rtype: str
		"""
		return self._displayName

	@property
	def className(self) -> str:
		"""Name of the class object.
		@return: class name or empty string
		@rtype: str
		"""
		return self._className

	@property
	def moduleName(self) -> str:
		"""The name of the module to which the class object belongs.
		@return: module name
		@rtype: str
		"""
		return self._moduleName

	@property
	def scriptName(self) -> str:
		"""The name of the function associated with the input gesture.
		@return: script name
		@rtype: str
		"""
		return self._scriptName

	@override
	def __eq__(self, other: object) -> bool:
		"""Comparison of objects for equality.
		@param other: an object that represents another input gesture
		@type other: object
		@return: the result of comparing the expression [self==other]
		@rtype: bool
		"""
		if not isinstance(other, Gesture):
			return False
		return (
			self.gesture == other.gesture
			and self.displayName == other.displayName
			and self.moduleName == other.moduleName
			and self.scriptName == other.scriptName
		)

	@override
	def __repr__(self) -> str:
		"""Text presentation of input gesture object.
		@return: text presentation
		@rtype: str
		"""
		return "%s - %s/%s" % (
			self.gesture,
			self.category or self.moduleName,
			self.displayName or self.scriptName,
		)


class Gestures:
	"""Presentation of the input gestures collection."""

	def __init__(self) -> None:
		"""Initialization of internal fields."""
		super().__init__()
		self._all: list[Gesture] = []

	def __len__(self) -> int:
		"""The number of gestures in collection.
		@return: length of the collection
		@rtype: int
		"""
		return self._all.__len__()

	def __getitem__(self, index: int) -> Gesture:
		"""Gesture from the collection under a given index.
		@param index: index of the input gesture in the collection
		@type index: int
		@return: input gesture from collection under a given index
		@rtype: Gesture
		"""
		return self._all[index]

	def __iter__(self) -> Iterator[Gesture]:
		"""Iterator of Gesture objects from collection.
		@return: all Gesture objects from collection
		@rtype: Iterator[Gesture]
		"""
		for gesture in self._all:
			yield gesture

	def __contains__(self, obj: Gesture | None) -> bool:
		"""Indication of whether an Gesture object is present in the collection.
		@param obj: gesture object to search in the collection
		@type obj: Gesture | None
		@return: whether there is an object in the collection
		@rtype: bool
		"""
		for gesture in self._all:
			if obj == gesture:
				return True
		return False

	def append(self, obj: Gesture) -> None:
		"""Add Gesture object to the collection.
		@param obj: an input gesture that will be added to the collection
		@type obj: Gesture
		"""
		if not obj or obj in self:
			return
		self._all.append(obj)

	def initialize(self) -> None:
		"""Scan all input gestures used in NVDA.
		Procedure for scanning input gestures:
		1. Gestures binded to functions with text description (displayed in the "Input Gestures" dialog).
		2. Gestures related to functions without a text description.
		"""
		self.signed()
		self.unsigned()

	def signed(self) -> None:
		"""Scan gestures binded to functions with text description
		wich displayed in the "Input Gestures" dialog.
		"""
		import inputCore

		# The input manager of NVDA has incomplete type annotations
		mapping = cast(Any, inputCore).manager.getAllGestureMappings()
		for category in list(mapping):
			for script in mapping[category]:
				obj = mapping[category][script]
				for gest in obj.gestures:
					gesture = Gesture(
						gesture=gest,
						category=obj.category,
						displayName=obj.displayName,
						className=obj.className,
						moduleName=obj.moduleName,
						scriptName=obj.scriptName,
					)
					self.append(gesture)

	def unsigned(self) -> None:
		"""Scan gestures binded to functions without text description
		wich not displayed in the "Input Gestures" dialog.
		"""
		import globalPluginHandler

		# The global plugins of NVDA and their gesture maps have incomplete type annotations
		for plugin in cast(Any, globalPluginHandler).runningPlugins:
			for gest, obj in plugin._gestureMap.items():
				if obj and not obj.__doc__:
					gesture = Gesture(
						gesture=gest,
						displayName=obj.__doc__,
						moduleName=obj.__module__,
						scriptName=obj.__name__.replace("script_", ""),
					)
					self.append(gesture)


class FilteredGestures:
	"""Basic class for filtered collections of input gestures."""

	name: str = ""

	@property
	def title(self) -> str:
		"""The title of the window that displays a list of input gestures from the collection.
		@return: a text string representing the title of the window
		@rtype: str
		"""
		return self.name.replace("&", "")

	@property
	def menuItem(self) -> str:
		"""The name of the menu item that call the window to display the gesture collection.
		@return: a text string representing the name of the menu item
		@rtype: str
		"""
		return self.name + "..."

	def __len__(self) -> int:
		"""The number of input gestures in the collection.
		@return: length of the collection
		@rtype: int
		"""
		return len([item for item in self])

	def __iter__(self) -> Iterator[Gesture]:
		"""Consistently returns input gestures from the collection filtered by a certain property.
		The method must be overridden in the child class.
		@return: iterator of the filtered input gestures
		@rtype: Iterator[Gesture]
		"""
		raise NotImplementedError


@dataclass
class DuplicateGroup:
	"""The gestures bound to the same keys in the current keyboard layout, i.e. one duplicate.
	@ivar key: the identifier of the gesture without the current keyboard layout
	@ivar gestures: the gestures of the duplicate
	"""

	key: str
	gestures: list[Gesture]

	def categories(self) -> list[tuple[str, list[Gesture]]]:
		"""The gestures of the duplicate grouped by their categories, both sorted by name.
		@return: the category labels with their gestures
		@rtype: list[tuple[str, list[Gesture]]]
		"""
		categories: dict[str, list[Gesture]] = {}
		for gesture in self.gestures:
			categories.setdefault(gesture.categoryLabel, []).append(gesture)
		return [
			(category, sorted(gestures, key=lambda item: (item.displayName or item.scriptName).casefold()))
			for category, gestures in sorted(categories.items(), key=lambda item: item[0].casefold())
		]


def getLayoutSuffix() -> str:
	"""The current keyboard layout as it is written in the identifiers of the gestures, e.g. "(laptop)".
	@return: the layout in parentheses
	@rtype: str
	"""
	import config

	# The configuration of NVDA has no type annotations
	return "(%s)" % cast(Any, config.conf)["keyboard"]["keyboardLayout"]


class Duplicates(FilteredGestures):
	"""Collection of duplicate input gestures."""

	def groups(self) -> list[DuplicateGroup]:
		"""The duplicates: the gestures grouped by their keys in the current keyboard layout,
		so a gesture for all layouts and the same gesture for the current layout are in one group.
		@return: the groups of the duplicate gestures, sorted by the identifiers of the gestures
		@rtype: list[DuplicateGroup]
		"""
		layout = getLayoutSuffix()
		groups: dict[str, list[Gesture]] = {}
		for gesture in self:
			groups.setdefault(gesture.gesture.replace(layout, ""), []).append(gesture)
		return [DuplicateGroup(key, gestures) for key, gestures in sorted(groups.items())]

	@override
	def __iter__(self) -> Iterator[Gesture]:
		"""Collection of the duplicated input gestures.
		@return: iterator of the duplicated input gestures
		@rtype: Iterator[Gesture]
		"""
		gestures = Gestures()
		gestures.initialize()
		# The current keyboard layout is removed from the gestures, so a gesture for all layouts
		# and the same gesture for the current layout are compared as the same keys
		layout = getLayoutSuffix()
		collection = [gt.gesture.replace(layout, "") for gt in gestures]
		for gest in gestures:
			if collection.count(gest.gesture.replace(layout, "")) > 1:
				yield gest


class Unsigned(FilteredGestures):
	"""Collection of input gestures binded to functions without a text description."""

	@override
	def __iter__(self) -> Iterator[Gesture]:
		"""Collection of the unsigned input gestures.
		@return: iterator of the unsigned input gestures
		@rtype: Iterator[Gesture]
		"""
		gestures = Gestures()
		gestures.unsigned()
		for gest in gestures:
			yield gest

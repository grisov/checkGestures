	#base.py
# Components required to work with input gestures collection
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>


class Gesture(object):
	"""Representation of one input gesture."""

	def __init__(self, gesture: str, category: str=None, displayName: str=None, className: str=None, moduleName: str=None, scriptName: str=None):
		"""Initialization of the main fields of the gesture description.
		@param gesture: text representation of the input gesture
		@type gesture: str
		@param category: the category to which the gesture-related function belongs
		@type category: str
		@param displayName: description of the gesture-related function
		@type displayName: str
		@param className: the name of the class to which the gesture-related function belongs
		@type className: str
		@param moduleName: the name of the module to which the associated class belongs
		@type moduleName: str
		@param scriptName: the script name of the gesture-bound function
		@type scriptName: str
		"""
		self._gesture = gesture or ''
		self._category = category or ''
		self._displayName = displayName or ''
		self._className = className or ''
		self._moduleName = moduleName or ''
		self._scriptName = scriptName or ''

	# Define methods
	gesture = lambda self: self._gesture
	category = lambda self: self._category
	displayName = lambda self: self._displayName
	className = lambda self: self._className
	moduleName = lambda self: self._moduleName
	scriptName = lambda self: self._scriptName

	# Define properties
	gesture = property(gesture)
	category = property(category)
	displayName = property(displayName)
	className = property(className)
	moduleName = property(moduleName)
	scriptName = property(scriptName)

	def __eq__(self, other: "Gesture") -> bool:
		"""Comparison of objects for equality.
		@param other: an object that represents another input gesture
		@type other: Gesture
		@return: the result of comparing the expression [self==other]
		@rtype: bool
		"""
		return self.gesture==other.gesture and \
			self.displayName==other.displayName and \
			self.moduleName==other.moduleName and \
			self.scriptName==other.scriptName

	def __repr__(self) -> str:
		"""Text presentation of input gesture object.
		@return: text presentation
		@rtype: str
		"""
		return "%s - %s / %s" % (self.gesture, self.category or self.moduleName, self.displayName or self.scriptName)


class Gestures(object):
	"""Presentation of the input gestures collection."""

	def __init__(self):
		"""Initialization of internal fields."""
		self._all = []

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

	def __iter__(self) -> "generator[Gesture]":
		"""Generator of Gesture objects from collection.
		@return: all Gesture objects from collection
		@rtype: generator[Gesture]
		"""
		for gesture in self._all:
			yield gesture

	def __contains__(self, obj: Gesture) -> bool:
		"""Indication of whether an Gesture object is present in the collection.
		@param obj: gesture object to search in the collection
		@type obj: Gesture
		@return: whether there is an object in the collection
		@rtype: bool
		"""
		for gesture in self._all:
			if obj==gesture:
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
		mapping = inputCore.manager.getAllGestureMappings()
		for category in list(mapping):
			for script in mapping[category]:
				obj = mapping[category][script]
				for gest in obj.gestures:
					gesture = Gesture(
						gesture = gest,
						category = obj.category,
						displayName = obj.displayName,
						className = obj.className,
						moduleName = obj.moduleName,
						scriptName = obj.scriptName
					)
					self.append(gesture)

	def unsigned(self) -> None:
		"""Scan gestures binded to functions without text description
		wich not displayed in the "Input Gestures" dialog.
		"""
		import globalPluginHandler
		for plugin in globalPluginHandler.runningPlugins:
			for gest,obj in plugin._gestureMap.items():
				if obj and not obj.__doc__:
					gesture = Gesture(
						gesture = gest,
						displayName = obj.__doc__,
						moduleName = obj.__module__,
						scriptName = obj.__name__.replace("script_", '')
					)
					self.append(gesture)


class FilteredGestures(object):
	"""Basic class for filtered collections of input gestures."""
	name = ""

	@property
	def title(self):
		"""The title of the window that displays a list of input gestures from the collection."""
		return self.name.replace('&', '')

	@property
	def menuItem(self):
		"""The name of the menu item that call the window to display the gesture collection."""
		return self.name + "..."

	def __len__(self) -> int:
		"""The number of input gestures in the collection.
		@return: length of the collection
		@rtype: int
		"""
		return len([item for item in self])

	def __iter__(self) -> "generator[Gesture]":
		"""Consistently returns input gestures from the collection filtered by a certain property.
		The method must be overridden in the child class.
		@return: generator of the filtered input gestures
		@rtype: generator[Gesture]
		"""
		raise NotImplementedError


class Duplicates(FilteredGestures):
	"""Collection of duplicate input gestures."""

	def __iter__(self) -> "generator[Gesture]":
		"""Collection of the duplicated input gestures.
		@return: generator of the duplicated input gestures
		@rtype: generator[Gesture]
		"""
		import config
		gestures = Gestures()
		gestures.initialize()
		collection = [item.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], '') for item in gestures]
		for gest in gestures:
			if collection.count(gest.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], ''))>1:
				yield gest


class Unsigned(FilteredGestures):
	"""Collection of input gestures binded to functions without a text description."""

	def __iter__(self) -> "generator[Gesture]":
		"""Collection of the unsigned input gestures.
		@return: generator of the unsigned input gestures
		@rtype: generator[Gesture]
		"""
		import config
		gestures = Gestures()
		gestures.unsigned()
		collection = [item.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], '') for item in gestures]
		for gest in gestures:
			yield gest

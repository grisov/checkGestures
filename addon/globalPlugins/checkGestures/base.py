#gestures.py
# Components required to work with input gestures collection
# A part of the NVDA Check Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>


class Gesture(object):

	def __init__(self, gesture: str, category: str=None, displayName: str=None, className: str=None, moduleName: str=None, scriptName: str=None):
		self._gesture = gesture or ''
		self._category = category or ''
		self._displayName = displayName or ''
		self._className = className or ''
		self._moduleName = moduleName or ''
		self._scriptName = scriptName or ''

	gesture = lambda self: self._gesture
	category = lambda self: self._category
	displayName = lambda self: self._displayName
	className = lambda self: self._className
	moduleName = lambda self: self._moduleName
	scriptName = lambda self: self._scriptName

	gesture = property(gesture)
	category = property(category)
	displayName = property(displayName)
	className = property(className)
	moduleName = property(moduleName)
	scriptName = property(scriptName)

	def __eq__(self, other) -> bool:
		return self.gesture==other.gesture and \
			self.displayName==other.displayName and \
			self.moduleName==other.moduleName and \
			self.scriptName==other.scriptName

	def __repr__(self) -> str:
		return "%s - %s / %s" % (self.gesture, self.category or self.moduleName, self.displayName or self.scriptName)


class Gestures(object):

	def __init__(self):
		self._all = []

	def __len__(self) -> int:
		return self._all.__len__()

	def __getitem__(self, index: int):
		return self._all[index]

	def __iter__(self):
		for gesture in self._all:
			yield gesture

	def __contains__(self, obj: Gesture) -> bool:
		for gesture in self._all:
			if obj==gesture:
				return True
		return False

	def append(self, obj: Gesture) -> None:
		if not obj or obj in self:
			return
		self._all.append(obj)

	def initialize(self) -> None:
		self.signed()
		self.unsigned()

	def signed(self) -> None:
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
		import globalPluginHandler
		for plugin in globalPluginHandler.runningPlugins:
			for gest,obj in plugin._gestureMap.items():
				gesture = Gesture(
					gesture = gest,
					displayName = obj.__doc__,
					moduleName = obj.__module__,
					scriptName = obj.__name__.replace("script_", '')
				)
				self.append(gesture)

	def duplicates(self):
		import config
		collection = [item.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], '') for item in self._all]
		for gest in self._all:
			if collection.count(gest.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], ''))>1:
				yield gest

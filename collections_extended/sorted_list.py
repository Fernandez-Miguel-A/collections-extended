"""SortedList class definition."""

import bisect
from collections import MutableSequence

from . import _compat

class SortedList(MutableSequence):
	"""Extends list and keeps values in sorted order.

	A key can be specified like for sorted.

	All list methods are inherited but raise a ValueError if they result in
	inserting a value in the wrong order.

	SortedList cannot enforce correct ordering after mutable elements are
	added then modified.
	"""

	def __init__(self, iterable=None, key=None, reversed=False):
		self._data = list(iterable or [])
		self.sort(key=key, reversed=reversed)

	def sort(self, key=None, reversed=False):
		self._data.sort(key=key, reverse=reversed)
		self._key = key
		self._reversed = reversed
		if self._key is not None:
			self._keys = [self.key(v) for v in self._data]
		else:
			self._keys = self._data

	@property
	def key(self):
		if self._key is None:
			return lambda x: x
		else:
			return self._key

	@key.setter
	def key(self, new_value):
		if new_value != self._key:
			self.sort(key=new_value, reversed=self.reversed)

	@property
	def reversed(self):
		return self._reversed

	@reversed.setter
	def reversed(self, new_value):
		if new_value != self._reversed:
			self.reverse()

	def reverse(self):
		self._data.reverse()
		if self._keys is not self._data:
			self._keys.reverse()
		self._reversed = not self._reversed

	def __str__(self):
		return str(self._data)

	def __repr__(self):
		return 'SortedList({data!r})'.format(data=self._data)

	# Implement Container
	def __contains__(self, value):
		try:
			self.index(value)
		except ValueError:
			return False
		else:
			return True

	# Implement Sized
	def __len__(self):
		return len(self._data)

	# Implement Sequence
	def __getitem__(self, index):
		return self._data.__getitem__(index)

	def count(self, value, start=0, end=None):
		out = 0
		min_i, max_i = self._get_min_max_index(value, start, end)
		# Have to search a range because multiple values may have the same key value
		for i in range(min_i, max_i):
			if self._data[i] == value:
				out += 1
		return out

	# Implement MutableSequence
	def __setitem__(self, index, value):
		value_key = self.key(value)
		if index - 1 >= 0 and value_key < self._keys[index - 1]:
			raise ValueError
		if index + 1 < len(self) and value_key > self._keys[index + 1]:
			raise ValueError
		self._data[index] = value
		self._keys[index] = value_key

	def __delitem__(self, index):
		self._data.__delitem__(index)
		if self._keys is not self._data:
			self._keys.__delitem__(index)

	def _insert(self, index, value, value_key):
		self._data.insert(index, value)
		if self._keys is not self._data:
			self._keys.insert(value_key)

	def insert(self, index, value):
		value_key = self.key(value)
		if index - 1 >= 0 and value_key < self._keys[index - 1]:
			raise ValueError
		if index + 1 < len(self) and value_key > self._keys[index + 1]:
			raise ValueError
		self._insert(index, value, value_key)

	def add_left(self, value):
		value_key = self.key(value)
		index = bisect.bisect_left(self._keys, value_key)
		self._insert(index, value, value_key)

	def add_right(self, value):
		value_key = self.key(value)
		index = bisect.bisect_right(self._keys, value_key)
		self._insert(index, value, value_key)

	add = add_right

	def index(self, value, start=0, stop=None):
		"""Return the index of the first occurence of value."""
		min_i, max_i = self._get_min_max_index(value, start, stop)
		# Have to search a range because multiple values may have the same key value
		for i in range(min_i, max_i):
			if self._data[i] == value:
				return i
		raise ValueError

	def _get_min_max_index(self, value, start, stop):
		value_key = self.key(value)
		# Can't pass a stop value = None here because of a bug in python
		if stop is None:
			stop = len(self)
		min_i = bisect.bisect_left(self._keys, value_key, lo=start, hi=stop)
		max_i = bisect.bisect_right(self._keys, value_key, lo=start, hi=stop)
		return min_i, max_i

	def __eq__(self, other):
		if not isinstance(other, SortedList):
			return False
		return self._data == other._data

	def __ne__(self, other):
		if not isinstance(other, SortedList):
			return True
		return self._data != other._data

	def __gt__(self, other):
		if not isinstance(other, SortedList):
			_compat.handle_rich_comp_not_implemented()
		return self._data > other._data

	def __ge__(self, other):
		if not isinstance(other, SortedList):
			_compat.handle_rich_comp_not_implemented()
		return self._data >= other._data

	def __lt__(self, other):
		if not isinstance(other, SortedList):
			_compat.handle_rich_comp_not_implemented()
		return self._data < other._data

	def __le__(self, other):
		if not isinstance(other, SortedList):
			_compat.handle_rich_comp_not_implemented()
		return self._data <= other._data
